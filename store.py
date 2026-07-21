import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue

from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
from normalize import Paper

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

EMBED_DIM = 1024  # BGE-M3's dense output size


def ensure_qdrant_collection() -> None:
    existing = [c.name for c in qdrant.get_collections().collections]
    if QDRANT_COLLECTION not in existing:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )


def find_existing_id(paper: Paper) -> str | None:
    """Look up whether this paper (by DOI, or source+source_id when there's no
    DOI) is already stored, so re-runs update in place instead of duplicating."""
    key_field, key_value = ("doi", paper.doi) if paper.doi else ("source_id", paper.source_id)
    if not key_value:
        return None

    must = [FieldCondition(key=key_field, match=MatchValue(value=key_value))]
    if key_field == "source_id":
        must.append(FieldCondition(key="source", match=MatchValue(value=paper.source)))

    hits, _ = qdrant.scroll(
        collection_name=QDRANT_COLLECTION,
        scroll_filter=Filter(must=must),
        limit=1,
    )
    return str(hits[0].id) if hits else None


def store_paper(paper: Paper, embedding: list[float]) -> str:
    """Upsert one paper into Qdrant: vector + full metadata as payload.
    `embedding` should be computed from the abstract when present, or the
    title as a fallback (see main.py) -- every paper needs *some* vector to
    be stored at all, since there's no separate metadata table anymore."""
    existing_id = find_existing_id(paper)
    paper_id = existing_id or str(uuid.uuid4())

    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=paper_id,
                vector=embedding,
                payload={
                    "title": paper.title,
                    "doi": paper.doi,
                    "authors": paper.authors,
                    "pub_date": paper.pub_date,
                    "source": paper.source,
                    "source_id": paper.source_id,
                    "url": paper.url,
                    "origin": paper.origin,  # 'scraped' or 'user_upload'
                    "abstract": paper.abstract,  # may be None if the source didn't have one
                },
            )
        ],
    )
    return paper_id
