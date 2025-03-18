import logging
import json
from typing import Dict, Any, List, Optional
from ..qdrant_client import QdrantClientWrapper
from mcp.types import TextContent
from qdrant_client.http.models import PointStruct

class VectorTools(QdrantClientWrapper):
    def register_tools(self, mcp: Any):
        """Register vector search related tools."""
        
        @mcp.tool(description="Search for similar vectors in a collection")
        async def search_vectors(
            collection_name: str,
            vector: List[float],
            limit: int = 10,
            with_vectors: bool = False
        ) -> list[TextContent]:
            """
            Search for similar vectors in a collection.
            
            Args:
                collection_name: Name of the collection
                vector: Query vector for similarity search
                limit: Maximum number of results to return
                with_vectors: Whether to include vector data in the response
            """
            self.logger.info(f"Searching vectors in collection {collection_name}")
            try:
                results = self.client.search(
                    collection_name=collection_name,
                    query_vector=vector,
                    limit=limit,
                    with_vectors=with_vectors
                )
                return [TextContent(type="text", text=str(results))]
            except Exception as e:
                self.logger.error(f"Error searching vectors: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Upload vectors to a collection")
        async def upsert_vectors(
            collection_name: str,
            vectors: List[List[float]],
            ids: List[str],
            metadata: Optional[List[Dict[str, Any]]] = None
        ) -> list[TextContent]:
            """
            Upload vectors to a collection.
            
            Args:
                collection_name: Name of the collection
                vectors: List of vectors to upload
                ids: List of IDs for the vectors
                metadata: Optional metadata for each vector
            """
            self.logger.info(f"Upserting vectors to collection {collection_name}")
            try:
                points = []
                
                # Prepare metadata list if not provided
                if metadata is None:
                    metadata = [{} for _ in range(len(vectors))]
                
                # Create point objects
                for i in range(len(vectors)):
                    points.append(
                        PointStruct(
                            id=ids[i],
                            vector=vectors[i],
                            payload=metadata[i] if i < len(metadata) else {}
                        )
                    )
                
                operation_info = self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                return [TextContent(type="text", text=f"Vectors uploaded successfully: {operation_info}")]
            except Exception as e:
                self.logger.error(f"Error upserting vectors: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
                
        @mcp.tool(description="Search collection with filter")
        async def filter_search(
            collection_name: str,
            filter_json: str,
            limit: int = 10
        ) -> list[TextContent]:
            """
            Search for points in a collection using filters.
            
            Args:
                collection_name: Name of the collection
                filter_json: JSON string representing the filter condition
                limit: Maximum number of results to return
            """
            self.logger.info(f"Searching with filter in collection {collection_name}")
            try:
                # Parse filter JSON string to dict
                filter_dict = json.loads(filter_json)
                
                results = self.client.scroll(
                    collection_name=collection_name,
                    limit=limit,
                    filter=filter_dict
                )
                
                return [TextContent(type="text", text=str(results))]
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid filter JSON: {e}")
                return [TextContent(type="text", text=f"Error: Invalid filter JSON - {str(e)}")]
            except Exception as e:
                self.logger.error(f"Error searching with filter: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")] 