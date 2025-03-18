import logging
import json
from typing import Dict, Any, List, Optional
from ..qdrant_client import QdrantClientWrapper
from mcp.types import TextContent

class PointTools(QdrantClientWrapper):
    def register_tools(self, mcp: Any):
        """Register point-related tools."""
        
        @mcp.tool(description="Get points from a collection")
        async def get_points(
            collection_name: str,
            ids: List[str],
            with_vectors: bool = False
        ) -> list[TextContent]:
            """
            Get points by their IDs from a collection.
            
            Args:
                collection_name: Name of the collection
                ids: List of point IDs to retrieve
                with_vectors: Whether to include vector data in the response
            """
            self.logger.info(f"Getting points from collection {collection_name} with IDs: {ids}")
            try:
                points = self.client.retrieve(
                    collection_name=collection_name,
                    ids=ids,
                    with_vectors=with_vectors
                )
                return [TextContent(type="text", text=str(points))]
            except Exception as e:
                self.logger.error(f"Error getting points: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Delete points from a collection")
        async def delete_points(
            collection_name: str,
            ids: List[str]
        ) -> list[TextContent]:
            """
            Delete points by their IDs from a collection.
            
            Args:
                collection_name: Name of the collection
                ids: List of point IDs to delete
            """
            self.logger.info(f"Deleting points from collection {collection_name} with IDs: {ids}")
            try:
                operation_info = self.client.delete(
                    collection_name=collection_name,
                    points_selector=ids
                )
                return [TextContent(type="text", text=f"Points deleted successfully: {operation_info}")]
            except Exception as e:
                self.logger.error(f"Error deleting points: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
                
        @mcp.tool(description="Count points in a collection")
        async def count_points(collection_name: str) -> list[TextContent]:
            """
            Count the number of points in a collection.
            
            Args:
                collection_name: Name of the collection
            """
            self.logger.info(f"Counting points in collection: {collection_name}")
            try:
                count = self.client.count(collection_name=collection_name)
                return [TextContent(type="text", text=f"Count: {count.count}")]
            except Exception as e:
                self.logger.error(f"Error counting points: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")] 