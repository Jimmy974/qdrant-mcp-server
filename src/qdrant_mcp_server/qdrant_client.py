import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

class QdrantClientWrapper:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.client = self._create_qdrant_client()
        # Get default collection name from environment
        self.default_collection = os.getenv("DEFAULT_COLLECTION_NAME", "default_collection")
        self.logger.info(f"Using default collection: {self.default_collection}")

    def _get_qdrant_config(self):
        """Get Qdrant configuration from environment variables."""
        # Load environment variables from .env file
        load_dotenv()
        config = {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": os.getenv("QDRANT_PORT", 6333),
            "api_key": os.getenv("QDRANT_API_KEY", ""),
            "verify_ssl": os.getenv("QDRANT_VERIFY_SSL", "True").lower() in ("true", "1", "yes")
        }
        
        return config

    def _create_qdrant_client(self) -> QdrantClient:
        """Create and return a Qdrant client using configuration from environment."""
        config = self._get_qdrant_config()
        
        client_kwargs = {
            "host": config["host"],
        }
        
        # Add port if specified (could be empty for cloud services)
        use_https = False
        if config["port"] and str(config["port"]).strip():
            try:
                port_value = int(config["port"])
                client_kwargs["port"] = port_value
                # Auto-detect HTTPS if port is 443
                if port_value == 443:
                    use_https = True
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid port value: {config['port']}, ignoring")
        
        # Determine if we should use HTTPS
        # 1. If host starts with https://, use HTTPS
        if client_kwargs["host"].startswith("https://"):
            use_https = True
            # Remove the protocol from the host
            client_kwargs["host"] = client_kwargs["host"].replace("https://", "")
        elif client_kwargs["host"].startswith("http://"):
            use_https = False
            # Remove the protocol from the host
            client_kwargs["host"] = client_kwargs["host"].replace("http://", "")
        
        # Set https parameter
        client_kwargs["https"] = use_https
        
        # Set verify parameter for SSL verification
        client_kwargs["verify"] = config["verify_ssl"]
        
        # Add API key if provided
        if config["api_key"]:
            client_kwargs["api_key"] = config["api_key"]
            
        try:
            self.logger.info(f"Connecting to Qdrant at {config['host']} (HTTPS: {use_https}, Verify SSL: {config['verify_ssl']})")
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