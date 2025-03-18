import pytest
import numpy as np

def test_embedding_model_initialization(embedding_model, test_logger):
    """Test that the embedding model initializes correctly."""
    assert embedding_model is not None
    assert embedding_model.model is not None
    assert embedding_model.vector_size > 0
    test_logger.info(f"Embedding model vector size: {embedding_model.vector_size}")

def test_embed_single_text(embedding_model, test_logger):
    """Test embedding a single text."""
    text = "This is a test sentence."
    embeddings = embedding_model.embed_text(text)
    
    # Check that we got a list with one embedding
    assert isinstance(embeddings, list)
    assert len(embeddings) == 1
    
    # Check the embedding shape
    embedding = embeddings[0]
    assert isinstance(embedding, list)
    assert len(embedding) == embedding_model.vector_size
    
    # Check that embeddings are floats
    assert all(isinstance(x, float) for x in embedding)
    
    test_logger.info(f"Successfully embedded single text to vector of size {len(embedding)}")

def test_embed_multiple_texts(embedding_model, sample_texts, test_logger):
    """Test embedding multiple texts."""
    embeddings = embedding_model.embed_text(sample_texts)
    
    # Check that we got a list with the right number of embeddings
    assert isinstance(embeddings, list)
    assert len(embeddings) == len(sample_texts)
    
    # Check each embedding
    for i, embedding in enumerate(embeddings):
        assert isinstance(embedding, list)
        assert len(embedding) == embedding_model.vector_size
        assert all(isinstance(x, float) for x in embedding)
    
    test_logger.info(f"Successfully embedded {len(sample_texts)} texts")

def test_embeddings_are_different(embedding_model, sample_texts, test_logger):
    """Test that different texts produce different embeddings."""
    embeddings = embedding_model.embed_text(sample_texts)
    
    # Compare each embedding with the others
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Convert to numpy arrays for easier calculation
            emb_i = np.array(embeddings[i])
            emb_j = np.array(embeddings[j])
            
            # Calculate cosine similarity
            dot_product = np.dot(emb_i, emb_j)
            norm_i = np.linalg.norm(emb_i)
            norm_j = np.linalg.norm(emb_j)
            similarity = dot_product / (norm_i * norm_j)
            
            # Embeddings should be different but still have some similarity 
            # (they're all about capitals)
            assert similarity < 0.99  # Not nearly identical
            assert similarity > 0.5   # But still somewhat similar due to related content
            
            test_logger.info(f"Similarity between text {i} and {j}: {similarity:.4f}")

def test_similar_texts_have_similar_embeddings(embedding_model, test_logger):
    """Test that similar texts have similar embeddings."""
    text1 = "What is the capital of France?"
    text2 = "Tell me the capital city of France."
    text3 = "The weather in Australia is nice today."
    
    emb1 = np.array(embedding_model.embed_text(text1)[0])
    emb2 = np.array(embedding_model.embed_text(text2)[0])
    emb3 = np.array(embedding_model.embed_text(text3)[0])
    
    # Calculate similarities
    sim_1_2 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    sim_1_3 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
    
    # Similar questions should have higher similarity than unrelated questions
    assert sim_1_2 > sim_1_3
    
    test_logger.info(f"Similarity between similar texts: {sim_1_2:.4f}")
    test_logger.info(f"Similarity between different texts: {sim_1_3:.4f}") 