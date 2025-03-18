import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

class QdrantClientWrapper:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.client = self._create_qdrant_client()

    def _get_qdrant_config(self):
        """Get Qdrant configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        config = {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": os.getenv("QDRANT_PORT", 6333),
            "api_key": os.getenv("QDRANT_API_KEY", "")
        }
        
        return config

    def _create_qdrant_client(self) -> QdrantClient:
        """Create and return a Qdrant client using configuration from environment."""
        config = self._get_qdrant_config()
        
        client_kwargs = {
            "host": config["host"],
            "port": int(config["port"]),
        }
        
        # Add API key if provided
        if config["api_key"]:
            client_kwargs["api_key"] = config["api_key"]
            
        try:
            client = QdrantClient(**client_kwargs)
            # Test connection
            client.get_collections()
            self.logger.info("Successfully connected to Qdrant")
            return client
        except UnexpectedResponse as e:
            self.logger.error(f"Failed to connect to Qdrant: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Error creating Qdrant client: {e}")
            raise e 