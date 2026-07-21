import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "papers_abstracts")

SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY") or None
EMBED_MODEL_CACHE_DIR = os.getenv("EMBED_MODEL_CACHE_DIR") or None  # None = library default (~/.cache/huggingface)
CORE_API_KEY = os.getenv("CORE_API_KEY")
SPRINGER_API_KEY = os.getenv("SPRINGER_API_KEY")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
