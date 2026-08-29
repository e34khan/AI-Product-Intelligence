from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # small, runs fine on CPU, outputs 384 dim vectors

# loading the model reads it from disk and sets it up in memory, which takes a
# moment, so we only want to do it once per process rather than every call
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()  # numpy arrays to plain python lists, so postgres can store them
