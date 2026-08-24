from sentence_transformers import SentenceTransformer
MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model

def create_embeddings(texts): # Convert text into vector embeddings.
    model = get_model()

    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )


def create_query_embedding(query): # Create an embedding for a user's question.
    model = get_model()
    
    return model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )