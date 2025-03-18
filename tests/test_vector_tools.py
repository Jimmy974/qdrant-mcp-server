import pytest
import json
import uuid
import os
import numpy as np
from qdrant_mcp_server.tools.vector import VectorTools
from qdrant_mcp_server.embedding import EmbeddingModel

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
def vector_tools(test_logger):
    """Create a VectorTools instance for testing."""
    # Force SSL verification off for tests
    os.environ["QDRANT_VERIFY_SSL"] = "False"
    return VectorTools(test_logger)

@pytest.fixture
def mock_mcp():
    """Create a mock MCP instance."""
    return MockMCP()

@pytest.fixture
def registered_tools(vector_tools, mock_mcp):
    """Register tools with the mock MCP and return them."""
    vector_tools.register_tools(mock_mcp)
    return mock_mcp.registered_tools

async def test_upsert_vectors(registered_tools, clean_test_collection, sample_vectors, 
                              sample_ids, sample_metadata, test_logger):
    """Test uploading vectors to a collection."""
    upsert_vectors = registered_tools["upsert_vectors"]
    
    # Test with metadata
    result = await upsert_vectors(
        collection_name=clean_test_collection,
        vectors=sample_vectors,
        ids=sample_ids,
        metadata=sample_metadata
    )
    
    # Check response
    assert result is not None
    assert len(result) > 0
    assert "Vectors uploaded successfully" in result[0].text
    
    test_logger.info(f"Uploaded {len(sample_vectors)} vectors with metadata")
    
    # Test without metadata
    subset_vectors = sample_vectors[:2]
    subset_ids = [str(uuid.uuid4()) for _ in range(2)]
    
    result = await upsert_vectors(
        collection_name=clean_test_collection,
        vectors=subset_vectors,
        ids=subset_ids
    )
    
    # Check response
    assert "Vectors uploaded successfully" in result[0].text
    
    test_logger.info(f"Uploaded {len(subset_vectors)} vectors without metadata")

async def test_search_vectors(registered_tools, clean_test_collection, sample_vectors, 
                             sample_ids, sample_metadata, test_logger):
    """Test searching for similar vectors."""
    upsert_vectors = registered_tools["upsert_vectors"]
    search_vectors = registered_tools["search_vectors"]
    
    # First, store some vectors
    await upsert_vectors(
        collection_name=clean_test_collection,
        vectors=sample_vectors,
        ids=sample_ids,
        metadata=sample_metadata
    )
    
    # Search using one of the vectors
    query_vector = sample_vectors[0]
    result = await search_vectors(
        collection_name=clean_test_collection,
        vector=query_vector,
        limit=3
    )
    
    # Check response
    assert result is not None
    assert len(result) > 0
    
    # Should find the original vector with high similarity
    result_text = result[0].text
    test_logger.info(f"Search results: {result_text}")
    
    # The most similar vector should be the one we used for query (with score nearly 1.0)
    assert sample_ids[0] in result_text
    
    # Test with with_vectors=True
    result = await search_vectors(
        collection_name=clean_test_collection,
        vector=query_vector,
        limit=1,
        with_vectors=True
    )
    
    # Vector data should be included in the results
    assert "vector" in result[0].text
    
    test_logger.info("Search with vectors included successful")

async def test_filter_search(registered_tools, clean_test_collection, sample_vectors, 
                            sample_ids, sample_metadata, test_logger):
    """Test searching with metadata filters."""
    upsert_vectors = registered_tools["upsert_vectors"]
    filter_search = registered_tools["filter_search"]
    
    # First, store vectors with metadata
    await upsert_vectors(
        collection_name=clean_test_collection,
        vectors=sample_vectors,
        ids=sample_ids,
        metadata=sample_metadata
    )
    
    # Search with a filter for a specific country
    filter_json = json.dumps({
        "must": [
            {"key": "country", "match": {"value": "Germany"}}
        ]
    })
    
    result = await filter_search(
        collection_name=clean_test_collection,
        filter_json=filter_json,
        limit=10
    )
    
    # Check response
    assert result is not None
    
    # Should find only the German entry
    result_text = result[0].text
    test_logger.info(f"Filter search results: {result_text}")
    
    # Get the ID of the German entry
    german_id = None
    for i, meta in enumerate(sample_metadata):
        if meta["country"] == "Germany":
            german_id = sample_ids[i]
    
    assert german_id in result_text
    
    # Test with a population filter
    filter_json = json.dumps({
        "must": [
            {"key": "population", "range": {"gt": 3.0}}
        ]
    })
    
    result = await filter_search(
        collection_name=clean_test_collection,
        filter_json=filter_json,
        limit=10
    )
    
    # Should find entries with population > 3.0
    result_text = result[0].text
    high_pop_countries = [meta["country"] for i, meta in enumerate(sample_metadata) 
                         if meta["population"] > 3.0]
    
    for country in high_pop_countries:
        assert country in result_text 