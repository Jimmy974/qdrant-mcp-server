import logging
from typing import Dict, Any, Optional
from ..qdrant_client import QdrantClientWrapper
from mcp.types import TextContent

class CollectionTools(QdrantClientWrapper):
    def register_tools(self, mcp: Any):
        """Register collection-related tools."""
        
        @mcp.tool(description="List all collections in the Qdrant database")
        async def list_collections() -> list[TextContent]:
            """List all collections in the Qdrant database."""
            self.logger.info("Listing collections...")
            try:
                collections = self.client.get_collections()
                return [TextContent(type="text", text=str(collections))]
            except Exception as e:
                self.logger.error(f"Error listing collections: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get collection info")
        async def get_collection(collection_name: str) -> list[TextContent]:
            """
            Get information about a specific collection.
            
            Args:
                collection_name: Name of the collection
            """
            self.logger.info(f"Getting collection info: {collection_name}")
            try:
                collection = self.client.get_collection(collection_name=collection_name)
                return [TextContent(type="text", text=str(collection))]
            except Exception as e:
                self.logger.error(f"Error getting collection: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Create a new collection")
        async def create_collection(
            collection_name: str, 
            vector_size: int,
            distance: str = "Cosine"
        ) -> list[TextContent]:
            """
            Create a new collection in Qdrant.
            
            Args:
                collection_name: Name of the collection to create
                vector_size: Dimension of vectors to be stored
                distance: Distance function (Cosine, Euclid, Dot)
            """
            self.logger.info(f"Creating collection: {collection_name}")
            try:
                self.client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "default": {
                            "size": vector_size,
                            "distance": distance
                        }
                    }
                )
                return [TextContent(type="text", text=f"Collection {collection_name} created successfully")]
            except Exception as e:
                self.logger.error(f"Error creating collection: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Delete a collection")
        async def delete_collection(collection_name: str) -> list[TextContent]:
            """
            Delete a collection from Qdrant.
            
            Args:
                collection_name: Name of the collection to delete
            """
            self.logger.info(f"Deleting collection: {collection_name}")
            try:
                self.client.delete_collection(collection_name=collection_name)
                return [TextContent(type="text", text=f"Collection {collection_name} deleted successfully")]
            except Exception as e:
                self.logger.error(f"Error deleting collection: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")] 