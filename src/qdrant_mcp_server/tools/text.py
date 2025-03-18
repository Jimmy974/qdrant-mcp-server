import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from ..qdrant_client import QdrantClientWrapper
from ..embedding import EmbeddingModel
from mcp.types import TextContent
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Filter

class TextTools(QdrantClientWrapper):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        # Initialize the embedding model
        self.embedding_model = EmbeddingModel(logger)
        
    def register_tools(self, mcp: Any):
        """Register text-related tools."""
        
        @mcp.tool(description="Store text in the vector database")
        async def store_text(
            text: str,
            metadata: Optional[Dict[str, Any]] = None,
            collection_name: Optional[str] = None,
            point_id: Optional[str] = None
        ) -> list[TextContent]:
            """
            Convert text to an embedding vector and store it in the database.
            
            Args:
                text: The text to embed and store
                metadata: Optional metadata to store with the text
                collection_name: Collection name (uses default if not provided)
                point_id: Custom ID for the point (generates UUID if not provided)
            """
            collection = collection_name or self.default_collection
            
            # Generate embedding for the text
            self.logger.info(f"Generating embedding for text: {text[:50]}...")
            vector = self.embedding_model.embed_text(text)[0]
            
            # Create metadata if not provided
            if metadata is None:
                metadata = {}
            
            # Add the original text to metadata
            metadata["text"] = text
            
            # Generate point ID if not provided
            if point_id is None:
                point_id = str(uuid.uuid4())
                
            try:
                # Ensure collection exists (create if needed)
                try:
                    self.client.get_collection(collection)
                except Exception:
                    self.logger.info(f"Collection {collection} not found, creating...")
                    self.client.recreate_collection(
                        collection_name=collection,
                        vectors_config={
                            "default": {
                                "size": self.embedding_model.vector_size,
                                "distance": "Cosine"
                            }
                        }
                    )
                
                # Store the point
                self.client.upsert(
                    collection_name=collection,
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=metadata
                        )
                    ]
                )
                
                return [TextContent(type="text", text=f"Text stored successfully with ID: {point_id}")]
            except Exception as e:
                self.logger.error(f"Error storing text: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
                
        @mcp.tool(description="Search for similar text")
        async def search_similar_text(
            query: str,
            limit: int = 10,
            collection_name: Optional[str] = None,
            filter_json: Optional[str] = None
        ) -> list[TextContent]:
            """
            Convert query text to an embedding and find similar vectors.
            
            Args:
                query: The text query to search for
                limit: Maximum number of results to return
                collection_name: Collection name (uses default if not provided)
                filter_json: Optional JSON filter to apply to search
            """
            collection = collection_name or self.default_collection
            
            self.logger.info(f"Searching for text similar to: {query[:50]}...")
            
            try:
                # Generate embedding for query
                query_vector = self.embedding_model.embed_text(query)[0]
                
                # Parse filter if provided
                search_filter = None
                if filter_json:
                    try:
                        filter_dict = json.loads(filter_json)
                        search_filter = Filter(**filter_dict)
                    except Exception as e:
                        self.logger.error(f"Error parsing filter JSON: {e}")
                        return [TextContent(type="text", text=f"Error parsing filter: {str(e)}")]
                
                # Search for similar vectors
                results = self.client.search(
                    collection_name=collection,
                    query_vector=query_vector,
                    limit=limit,
                    filter=search_filter
                )
                
                # Format results nicely
                formatted_results = []
                for i, res in enumerate(results):
                    formatted_results.append({
                        "id": res.id,
                        "score": res.score,
                        "text": res.payload.get("text", "No text available"),
                        "metadata": {k: v for k, v in res.payload.items() if k != "text"}
                    })
                
                return [TextContent(type="text", text=json.dumps(formatted_results, indent=2))]
            except Exception as e:
                self.logger.error(f"Error searching for similar text: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
                
        @mcp.tool(description="Bulk store texts in the vector database")
        async def store_texts(
            texts: List[str],
            metadatas: Optional[List[Dict[str, Any]]] = None,
            collection_name: Optional[str] = None,
            point_ids: Optional[List[str]] = None
        ) -> list[TextContent]:
            """
            Convert multiple texts to embedding vectors and store them in the database.
            
            Args:
                texts: List of texts to embed and store
                metadatas: Optional list of metadata dicts (one per text)
                collection_name: Collection name (uses default if not provided)
                point_ids: Custom IDs for the points (generates UUIDs if not provided)
            """
            collection = collection_name or self.default_collection
            
            # Generate embeddings for all texts
            self.logger.info(f"Generating embeddings for {len(texts)} texts...")
            vectors = self.embedding_model.embed_text(texts)
            
            # Create metadata list if not provided
            if metadatas is None:
                metadatas = [{} for _ in range(len(texts))]
            
            # Generate point IDs if not provided
            if point_ids is None:
                point_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
                
            # Add the original texts to metadata
            for i, text in enumerate(texts):
                if i < len(metadatas):
                    metadatas[i]["text"] = text
                
            try:
                # Ensure collection exists (create if needed)
                try:
                    self.client.get_collection(collection)
                except Exception:
                    self.logger.info(f"Collection {collection} not found, creating...")
                    self.client.recreate_collection(
                        collection_name=collection,
                        vectors_config={
                            "default": {
                                "size": self.embedding_model.vector_size,
                                "distance": "Cosine"
                            }
                        }
                    )
                
                # Create points
                points = []
                for i in range(len(texts)):
                    points.append(
                        PointStruct(
                            id=point_ids[i],
                            vector=vectors[i],
                            payload=metadatas[i] if i < len(metadatas) else {"text": texts[i]}
                        )
                    )
                
                # Store the points
                self.client.upsert(
                    collection_name=collection,
                    points=points
                )
                
                return [TextContent(type="text", text=f"{len(texts)} texts stored successfully")]
            except Exception as e:
                self.logger.error(f"Error storing texts: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")] 