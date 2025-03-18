#!/usr/bin/env python3
"""
Simple script to check Qdrant connection before running tests.
"""
import os
import sys
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("connection_check")

def main():
    """Check connection to Qdrant server."""
    # Add the parent directory to sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    
    # Load environment from .env file
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        logger.info(f"Loading environment from: {env_file}")
        load_dotenv(env_file)
    else:
        logger.warning("No .env file found")
        return 1
    
    # Get Qdrant config from environment
    host = os.getenv("QDRANT_HOST")
    port = os.getenv("QDRANT_PORT")
    api_key = os.getenv("QDRANT_API_KEY")
    verify_ssl = os.getenv("QDRANT_VERIFY_SSL", "True").lower() in ("true", "1", "yes")
    
    # Build client kwargs
    client_kwargs = {
        "host": host
    }
    
    # Determine if we should use HTTPS
    use_https = False
    
    # Add port if specified (could be empty for cloud services)
    if port and str(port).strip():
        try:
            port_value = int(port)
            client_kwargs["port"] = port_value
            # Auto-detect HTTPS if port is 443
            if port_value == 443:
                use_https = True
        except (ValueError, TypeError):
            logger.warning(f"Invalid port value: {port}, ignoring")
    
    # Check if host starts with protocol
    if client_kwargs["host"].startswith("https://"):
        use_https = True
        # Remove the protocol from the host
        client_kwargs["host"] = client_kwargs["host"].replace("https://", "")
    elif client_kwargs["host"].startswith("http://"):
        use_https = False
        # Remove the protocol from the host
        client_kwargs["host"] = client_kwargs["host"].replace("http://", "")
    
    # Set https parameter based on port and host
    client_kwargs["https"] = use_https
    
    # Set verify parameter for SSL verification
    client_kwargs["verify"] = verify_ssl
    
    if api_key and api_key.strip():
        client_kwargs["api_key"] = api_key
    
    logger.info(f"Connecting to Qdrant at {host} (HTTPS: {use_https}, Verify SSL: {verify_ssl})")
    
    # Try to connect
    try:
        client = QdrantClient(**client_kwargs)
        collections = client.get_collections()
        logger.info(f"Successfully connected to Qdrant!")
        logger.info(f"Available collections: {collections}")
        return 0
    except UnexpectedResponse as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 