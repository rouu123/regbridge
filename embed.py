from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL_CACHE_DIR

# Downloads the model weights (~2GB) once on first run, then loads from
# local cache. Runs on CPU by default; will use GPU automatically if
# torch detects one. Set EMBED_MODEL_CACHE_DIR in .env to change where
# the weights get saved (defaults to ~/.cache/huggingface if unset).
_model = SentenceTransformer("BAAI/bge-m3", cache_folder=EMBED_MODEL_CACHE_DIR)


def embed_texts(texts: list[str], batch_size: int = 16) -> list[list[float]]:
    """Batch-embed a list of texts (abstracts, or titles as a fallback)."""
    if not texts:
        return []
    all_embeddings = []
    chunk_size = 10
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        chunk_vectors = _model.encode(chunk, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
        all_embeddings.extend(chunk_vectors.tolist())
    return all_embeddings
