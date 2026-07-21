"""
Run: python main.py

Edit QUERY / LIMIT_PER_SOURCE / SOURCES below and run again for a different search.
No CLI flags on purpose -- just constants, so it stays a one-file thing to tweak.
"""

from normalize import Paper
from embed import embed_texts
from store import store_paper, ensure_qdrant_collection

from sources import semantic_scholar, arxiv, openalex, core, springer, doaj

QUERY = "large language model hallucination"
LIMIT_PER_SOURCE = 20

# Comment out any source you don't have API keys for / don't want to hit.
SOURCES = {
    "semantic_scholar": semantic_scholar.fetch,
    "arxiv": arxiv.fetch,
    "openalex": openalex.fetch,
    "core": core.fetch,
    "springer": springer.fetch,
    "doaj": doaj.fetch,
}


def collect(query: str, limit: int) -> list[Paper]:
    all_papers: list[Paper] = []
    seen_keys: set[str] = set()

    for name, fetch_fn in SOURCES.items():
        try:
            results = fetch_fn(query, limit)
        except Exception as e:
            print(f"[{name}] skipped due to error: {e}")
            continue

        added = 0
        for paper in results:
            key = paper.dedupe_key()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            all_papers.append(paper)
            added += 1
        print(f"[{name}] fetched {len(results)}, added {added} new")

    return all_papers


def run(query: str = QUERY, limit: int = LIMIT_PER_SOURCE) -> None:
    ensure_qdrant_collection()

    papers = collect(query, limit)
    print(f"\nTotal unique papers: {len(papers)}")

    # Embed the abstract when we have one; fall back to the title so a paper
    # without an abstract still gets a vector and isn't silently dropped.
    texts = [p.abstract or p.title for p in papers]
    embeddings = embed_texts(texts) if texts else []

    stored = 0
    for paper, embedding in zip(papers, embeddings):
        store_paper(paper, embedding)
        stored += 1

    print(f"Stored {stored} papers in Qdrant (metadata + abstract as payload, vector from abstract or title).")


if __name__ == "__main__":
    run()
