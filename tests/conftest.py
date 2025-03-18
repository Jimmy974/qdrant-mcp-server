import os
import uuid
import pytest
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_mcp_server.embedding import EmbeddingModel
from qdrant_mcp_server.qdrant_client import QdrantClientWrapper

# Configure logging for tests
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("qdrant_test")

# Find the project root directory and .env file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_FILE = os.path.join(PROJECT_ROOT, '.env')

# Load environment variables
if os.path.exists(ENV_FILE):
    logger.info(f"Loading environment from: {ENV_FILE}")
    load_dotenv(ENV_FILE)
else:
    logger.warning(f".env file not found at {ENV_FILE}, using environment variables")
    load_dotenv()

@pytest.fixture
def test_logger():
    """Provide a logger for tests."""
    return logger

@pytest.fixture
def embedding_model(test_logger):
    """Provide an embedding model instance for tests."""
    return EmbeddingModel(test_logger)

@pytest.fixture
def test_collection_name():
    """Provide a test collection name."""
    # Use the default collection from .env or specify a test-specific one
    return os.getenv("TEST_COLLECTION_NAME", "test_collection")

@pytest.fixture
def qdrant_client(test_logger):
    """Provide a Qdrant client wrapper for tests."""
    client_wrapper = QdrantClientWrapper(test_logger)
    
    # Return both the wrapper and the underlying client
    return client_wrapper

@pytest.fixture
def clean_test_collection(qdrant_client, test_collection_name):
    """Ensure a clean test collection exists."""
    # Delete collection if it exists
    try:
        qdrant_client.client.delete_collection(test_collection_name)
        logger.info(f"Deleted existing test collection: {test_collection_name}")
    except Exception:
        logger.info(f"Test collection {test_collection_name} did not exist")
    
    # Create a fresh collection with the embedding model's vector size
    embedding_model = EmbeddingModel(logger)
    qdrant_client.client.recreate_collection(
        collection_name=test_collection_name,
        vectors_config={
            "default": {
                "size": embedding_model.vector_size,
                "distance": "Cosine"
            }
        }
    )
    logger.info(f"Created fresh test collection: {test_collection_name}")
    
    yield test_collection_name
    
    # Cleanup after tests
    try:
        qdrant_client.client.delete_collection(test_collection_name)
        logger.info(f"Cleaned up test collection: {test_collection_name}")
    except Exception as e:
        logger.error(f"Failed to clean up test collection: {e}")

@pytest.fixture
def sample_texts():
    """Provide sample texts for testing."""
    return [
        "Paris is the capital of France",
        "London is the capital of England",
        "Berlin is the capital of Germany",
        "Rome is the capital of Italy",
        "Madrid is the capital of Spain"
    ]

@pytest.fixture
def sample_metadata():
    """Provide sample metadata for testing."""
    return [
        {"country": "France", "continent": "Europe", "population": 2.1},
        {"country": "England", "continent": "Europe", "population": 8.9},
        {"country": "Germany", "continent": "Europe", "population": 3.6},
        {"country": "Italy", "continent": "Europe", "population": 2.8},
        {"country": "Spain", "continent": "Europe", "population": 3.2}
    ]

@pytest.fixture
def sample_vectors(embedding_model, sample_texts):
    """Generate sample vectors from the sample texts."""
    return embedding_model.embed_text(sample_texts)

@pytest.fixture
def sample_ids():
    """Generate sample IDs for vectors."""
    return [str(uuid.uuid4()) for _ in range(5)] 