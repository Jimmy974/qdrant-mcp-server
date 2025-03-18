# Qdrant MCP Server

An MCP server for interacting with [Qdrant](https://qdrant.tech/) vector database. This server provides tools for managing vectors, performing similarity searches, and automatic text-to-vector embedding using the MCP (Master Control Program) framework.

## Features

- Automatic text-to-vector embedding using FastEmbed
- Store and retrieve text content with vector search
- Use default collection configuration through environment variables
- Text similarity search by content
- Efficient embedding with optimized models

## Configuration

Create a `.env` file based on the `.env.example` template:

```
# Qdrant connection settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=
QDRANT_VERIFY_SSL=True  # Set to False if using self-signed certificates

# Default settings
DEFAULT_COLLECTION_NAME=default_collection
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

You can change the embedding model to any model supported by [FastEmbed](https://github.com/qdrant/fastembed).

## Usage

### Running locally

1. Install the package:
```
pip install -e .
```

2. Run the server:
```
qdrant-mcp-server
```

### Running with Docker

1. Build the Docker image:
```
docker build -t qdrant-mcp-server .
```

2. Run the container:
```
docker run -p 8000:8000 --env QDRANT_HOST=<your-qdrant-host> --env QDRANT_PORT=<your-qdrant-port> --env QDRANT_VERIFY_SSL=<True|False> qdrant-mcp-server
```

## Testing

This package includes a test suite to validate the functionality. To run the tests:

1. Install development dependencies:
```
pip install -e ".[dev]"
```

2. Run the tests:
```
cd tests
./run_tests.py
```

Alternatively, you can use pytest directly:
```
pytest -xvs tests/
```

### Using Self-Signed Certificates

If your Qdrant server uses a self-signed certificate, set `QDRANT_VERIFY_SSL=False` in your `.env` file or when running the Docker container. This disables SSL certificate verification.

## Tools

The server provides the following tools:

### Text Tools
- `store_text`: Convert text to an embedding vector and store it in the database
- `search_similar_text`: Convert query text to an embedding and find similar vectors
- `store_texts`: Convert multiple texts to embeddings and store them in batch

### Vector Tools
- `search_vectors`: Search for similar vectors in a collection
- `upsert_vectors`: Upload vectors to a collection
- `filter_search`: Search collection with metadata filters

### Point Tools
- `get_points`: Get points by their IDs from a collection
- `delete_points`: Delete points by their IDs from a collection
- `count_points`: Count the number of points in a collection

## Examples

### Storing text
```
await store_text(
    text="What is the capital of France?", 
    metadata={"category": "geography", "type": "question"}
)
```

### Searching for similar text
```
await search_similar_text(
    query="What is Paris the capital of?",
    limit=5
)
```

### Storing multiple texts
```
await store_texts(
    texts=["Paris is in France", "London is in England", "Berlin is in Germany"],
    metadatas=[
        {"category": "geography", "country": "France"},
        {"category": "geography", "country": "England"},
        {"category": "geography", "country": "Germany"}
    ]
) 