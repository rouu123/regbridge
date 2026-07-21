"""
Add a paper by hand (not from a scrape). Tags it origin='user_upload' so it's
distinguishable from scraped entries in Qdrant payloads.

Run: python add_manual.py
Edit the Paper(...) call below with your details, or import add_paper()
and call it from elsewhere (e.g. a small upload script/notebook).
"""

import uuid
from normalize import Paper
from embed import embed_texts
from store import store_paper, ensure_qdrant_collection


def add_paper(
    title: str,
    abstract: str | None = None,
    doi: str | None = None,
    authors: list[str] | None = None,
    pub_date: str | None = None,
    url: str | None = None,
) -> str:
    ensure_qdrant_collection()
    paper = Paper(
        title=title,
        source="user_upload",
        source_id=doi or str(uuid.uuid4()),  # dedupe key when there's no DOI
        doi=doi,
        authors=authors or [],
        pub_date=pub_date,
        abstract=abstract,
        url=url,
        origin="user_upload",
    )
    embedding = embed_texts([paper.abstract or paper.title])[0]
    paper_id = store_paper(paper, embedding)
    print(f"Stored '{title}' as {paper_id} (origin=user_upload)")
    return paper_id


if __name__ == "__main__":
    add_paper(
        title="Example manually-added paper",
        abstract="Replace this with the real abstract text.",
        doi=None,
        authors=["Author One", "Author Two"],
        pub_date="2026-01-15",
        url="https://example.com/paper.pdf",
    )
