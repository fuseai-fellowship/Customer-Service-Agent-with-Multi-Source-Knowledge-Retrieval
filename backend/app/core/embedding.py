from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=None)
def get_embedding_model():
    """
    Loads the Sentence Transformer model into memory.
    This function is cached, so the model is only loaded once.
    """
    print("Loading embedding model into memory...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding model loaded successfully.")
    return model

def generate_embedding(item_data: dict, category_name: str | None):
    """
    Creates a single text document from an item's details and generates an embedding.
    """
    model = get_embedding_model()

    document = (
        f"Name: {item_data.get('name', '')}. "
        f"Description: {item_data.get('description', '')}. "
        f"Category: {category_name or ''}. "
        f"Subcategory: {item_data.get('subcategory', '')}."
    )

    embedding_vector = model.encode(document).tolist()
    return embedding_vector