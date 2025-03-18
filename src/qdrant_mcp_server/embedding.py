import os
import logging
import numpy as np
from typing import List, Union
from dotenv import load_dotenv
from fastembed import TextEmbedding

class EmbeddingModel:
    _instance = None
    
    def __new__(cls, logger: logging.Logger = None):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, logger: logging.Logger = None):
        if self._initialized:
            return
            
        # Load environment variables
        load_dotenv()
        
        self.logger = logger or logging.getLogger(__name__)
        self.model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.logger.info(f"Initializing embedding model: {self.model_name}")
        
        try:
            self.model = TextEmbedding(model_name=self.model_name)
            
            # Get vector size by embedding a test string
            test_embedding = next(self.model.embed(["test"]))
            self.vector_size = len(test_embedding)
            
            self.logger.info(f"Model loaded successfully. Vector size: {self.vector_size}")
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            raise
            
        self._initialized = True
    
    def embed_text(self, text: Union[str, List[str]]) -> List[List[float]]:
        """
        Convert text or list of texts to embedding vectors.
        
        Args:
            text: A single text string or list of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if isinstance(text, str):
            text = [text]
            
        try:
            # Generate embeddings
            embeddings = list(self.model.embed(text))
            
            # Convert to list of lists if needed
            if isinstance(embeddings[0], np.ndarray):
                embeddings = [emb.tolist() for emb in embeddings]
                
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise 