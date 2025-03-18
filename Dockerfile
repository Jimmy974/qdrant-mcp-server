# Start with a Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy necessary files
COPY . .

# Install hatch to handle the build
RUN pip install hatch

# Clean dist directory before build
RUN rm -rf dist/*

# Use hatch to build the package and install it
RUN hatch build && pip install dist/*.whl

# Set environment variables required for the MCP server
# These can be overridden at runtime with docker run --env
ENV QDRANT_HOST="localhost"
ENV QDRANT_PORT="6333"
ENV QDRANT_API_KEY=""
ENV QDRANT_VERIFY_SSL="True"
ENV DEFAULT_COLLECTION_NAME="default_collection"
ENV EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"

# Expose the port the server is running on
EXPOSE 8000

# Command to run the server
ENTRYPOINT ["qdrant-mcp-server"] 