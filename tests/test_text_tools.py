import pytest
import json
import uuid
import os
from qdrant_mcp_server.tools.text import TextTools

class MockMCP:
    """Mock MCP class for testing tools."""
    
    def __init__(self):
        self.registered_tools = {}
    
    def tool(self, description=""):
        """Mock tool decorator."""
        def decorator(func):
            self.registered_tools[func.__name__] = func
            return func
        return decorator

@pytest.fixture
def text_tools(test_logger):
    """Create a TextTools instance for testing."""
    # Force SSL verification off for tests
    os.environ["QDRANT_VERIFY_SSL"] = "False"
    return TextTools(test_logger)

@pytest.fixture
def mock_mcp():
    """Create a mock MCP instance."""
    return MockMCP()

@pytest.fixture
def registered_tools(text_tools, mock_mcp):
    """Register tools with the mock MCP and return them."""
    text_tools.register_tools(mock_mcp)
    return mock_mcp.registered_tools

async def test_store_text(registered_tools, clean_test_collection, test_logger):
    """Test storing a single text as a vector."""
    store_text = registered_tools["store_text"]
    
    # Test without metadata
    result = await store_text(
        text="This is a test document",
        collection_name=clean_test_collection
    )
    
    # Check that we got a response
    assert result is not None
    assert len(result) > 0
    assert result[0].type == "text"
    assert "Text stored successfully with ID:" in result[0].text
    
    # Extract the ID for later use
    response_text = result[0].text
    point_id = response_text.split("ID: ")[1]
    
    test_logger.info(f"Stored text with ID: {point_id}")
    
    # Test with metadata and custom ID
    custom_id = str(uuid.uuid4())
    metadata = {"source": "test", "category": "example"}
    
    result = await store_text(
        text="This is another test document",
        metadata=metadata,
        collection_name=clean_test_collection,
        point_id=custom_id
    )
    
    # Check response
    assert "Text stored successfully with ID:" in result[0].text
    assert custom_id in result[0].text
    
    test_logger.info(f"Stored text with custom ID: {custom_id}")

async def test_search_similar_text(registered_tools, clean_test_collection, sample_texts, sample_metadata, test_logger):
    """Test searching for similar texts."""
    store_texts = registered_tools["store_texts"]
    search_similar_text = registered_tools["search_similar_text"]
    
    # First, store some sample texts
    result = await store_texts(
        texts=sample_texts,
        metadatas=sample_metadata,
        collection_name=clean_test_collection
    )
    
    assert result is not None
    assert "texts stored successfully" in result[0].text
    
    # Now search for something similar to the first text
    search_query = "What is the capital city of France?"
    result = await search_similar_text(
        query=search_query,
        limit=2,
        collection_name=clean_test_collection
    )
    
    # Check the response
    assert result is not None
    assert len(result) > 0
    
    # Parse the JSON response
    search_results = json.loads(result[0].text)
    
    # Should find the first text (about Paris) most similar
    assert len(search_results) > 0
    assert isinstance(search_results, list)
    assert "id" in search_results[0]
    assert "score" in search_results[0]
    assert "text" in search_results[0]
    assert "metadata" in search_results[0]
    
    # The best match should be the one about Paris
    assert "Paris" in search_results[0]["text"]
    assert search_results[0]["metadata"]["country"] == "France"
    
    test_logger.info(f"Search results: {json.dumps(search_results, indent=2)}")
    
    # Try search with filter
    filter_json = json.dumps({
        "must": [
            {"key": "country", "match": {"value": "Germany"}}
        ]
    })
    
    result = await search_similar_text(
        query="European capital",
        limit=1,
        collection_name=clean_test_collection,
        filter_json=filter_json
    )
    
    # Parse the JSON response
    filtered_results = json.loads(result[0].text)
    
    # Should only find the result about Berlin
    assert len(filtered_results) > 0
    assert "Berlin" in filtered_results[0]["text"]
    assert filtered_results[0]["metadata"]["country"] == "Germany"
    
    test_logger.info(f"Filtered search results: {json.dumps(filtered_results, indent=2)}")

async def test_store_texts(registered_tools, clean_test_collection, sample_texts, sample_metadata, test_logger):
    """Test storing multiple texts at once."""
    store_texts = registered_tools["store_texts"]
    
    # Store texts with metadata
    result = await store_texts(
        texts=sample_texts,
        metadatas=sample_metadata,
        collection_name=clean_test_collection
    )
    
    # Check response
    assert result is not None
    assert f"{len(sample_texts)} texts stored successfully" in result[0].text
    
    # Store texts with custom IDs
    custom_ids = [f"test-{i}" for i in range(3)]
    subset_texts = sample_texts[:3]
    
    result = await store_texts(
        texts=subset_texts,
        collection_name=clean_test_collection,
        point_ids=custom_ids
    )
    
    # Check response
    assert result is not None
    assert f"{len(subset_texts)} texts stored successfully" in result[0].text
    
    test_logger.info(f"Stored {len(sample_texts)} texts and {len(subset_texts)} texts with custom IDs") 