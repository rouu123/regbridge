from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL_CACHE_DIR

# Downloads the model weights (~2GB) once on first run, then loads from
# local cache. Runs on CPU by default; will use GPU automatically if
# torch detects one. Set EMBED_MODEL_CACHE_DIR in .env to change where
# the weights get saved (defaults to ~/.cache/huggingface if unset).
_model = SentenceTransformer("BAAI/bge-m3", cache_folder=EMBED_MODEL_CACHE_DIR)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of texts (abstracts, or titles as a fallback)."""
    if not texts:
        return []
    vectors = _model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()
