# Qdrant MCP Server

An MCP server for interacting with [Qdrant](https://qdrant.tech/) vector database. This server provides tools for managing collections, vectors, and performing similarity searches using the MCP (Master Control Program) framework.

## Features

- Create, list, and manage Qdrant collections
- Upload and search vectors
- Perform similarity search and filtering
- Manage vector points and metadata

## Configuration

Create a `.env` file based on the `.env.example` template:

```
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=
```

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
docker run -p 8000:8000 --env QDRANT_HOST=<your-qdrant-host> --env QDRANT_PORT=<your-qdrant-port> --env QDRANT_API_KEY=<your-api-key> qdrant-mcp-server
```

## Tools

The server provides the following tools:

### Collection Tools
- `list_collections`: List all collections in Qdrant
- `get_collection`: Get information about a specific collection
- `create_collection`: Create a new collection with specified vector dimension
- `delete_collection`: Delete a collection

### Vector Tools
- `search_vectors`: Search for similar vectors in a collection
- `upsert_vectors`: Upload vectors to a collection
- `filter_search`: Search collection with metadata filters

### Point Tools
- `get_points`: Get points by their IDs from a collection
- `delete_points`: Delete points by their IDs from a collection
- `count_points`: Count the number of points in a collection 