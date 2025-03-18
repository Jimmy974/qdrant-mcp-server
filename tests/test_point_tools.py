import pytest
import json
import uuid
import os
from qdrant_mcp_server.tools.point import PointTools
from qdrant_mcp_server.tools.vector import VectorTools

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
def point_tools(test_logger):
    """Create a PointTools instance for testing."""
    # Force SSL verification off for tests
    os.environ["QDRANT_VERIFY_SSL"] = "False"
    return PointTools(test_logger)

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
def point_registered_tools(point_tools, mock_mcp):
    """Register point tools with the mock MCP and return them."""
    point_tools.register_tools(mock_mcp)
    return mock_mcp.registered_tools

@pytest.fixture
def vector_registered_tools(vector_tools, mock_mcp):
    """Register vector tools with the mock MCP and return them."""
    vector_tools.register_tools(mock_mcp)
    return mock_mcp.registered_tools

@pytest.fixture
async def populated_collection(clean_test_collection, vector_registered_tools, 
                              sample_vectors, sample_ids, sample_metadata):
    """Prepare a collection with sample data for testing point operations."""
    upsert_vectors = vector_registered_tools["upsert_vectors"]
    
    # Store vectors with metadata
    await upsert_vectors(
        collection_name=clean_test_collection,
        vectors=sample_vectors,
        ids=sample_ids,
        metadata=sample_metadata
    )
    
    # Return collection name and sample IDs for later use
    return {
        "collection_name": clean_test_collection,
        "ids": sample_ids
    }

async def test_count_points(point_registered_tools, populated_collection, test_logger):
    """Test counting points in a collection."""
    count_points = point_registered_tools["count_points"]
    
    collection_name = populated_collection["collection_name"]
    all_ids = populated_collection["ids"]
    
    # Count all points
    result = await count_points(
        collection_name=collection_name
    )
    
    # Check response - should match the number of IDs we inserted
    assert result is not None
    assert len(result) > 0
    result_text = result[0].text
    
    # Extract count from text
    count_str = result_text.split(": ")[1]
    count = int(count_str)
    
    assert count == len(all_ids)
    
    test_logger.info(f"Counted {count} points in collection")

async def test_delete_points(point_registered_tools, populated_collection, test_logger):
    """Test deleting points by their IDs."""
    delete_points = point_registered_tools["delete_points"]
    count_points = point_registered_tools["count_points"]
    
    collection_name = populated_collection["collection_name"]
    all_ids = populated_collection["ids"]
    
    # Get initial count
    result = await count_points(collection_name=collection_name)
    initial_count = int(result[0].text.split(": ")[1])
    
    # Delete one point
    delete_id = all_ids[0]
    result = await delete_points(
        collection_name=collection_name,
        ids=[delete_id]
    )
    
    # Check response
    assert result is not None
    assert "Points deleted successfully" in result[0].text
    
    # Check count is reduced
    result = await count_points(collection_name=collection_name)
    new_count = int(result[0].text.split(": ")[1])
    assert new_count == initial_count - 1
    
    test_logger.info(f"Deleted point with ID: {delete_id}")
    
    # Delete multiple points
    delete_ids = all_ids[1:3]
    result = await delete_points(
        collection_name=collection_name,
        ids=delete_ids
    )
    
    # Check response
    assert "Points deleted successfully" in result[0].text
    
    # Check count is reduced again
    result = await count_points(collection_name=collection_name)
    final_count = int(result[0].text.split(": ")[1])
    assert final_count == new_count - len(delete_ids)
    
    test_logger.info(f"Deleted {len(delete_ids)} additional points") 