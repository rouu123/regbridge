import requests
from normalize import Paper
from config import SEMANTIC_SCHOLAR_API_KEY

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,externalIds,authors,abstract,publicationDate,url"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    resp = requests.get(
        BASE_URL,
        params={"query": query, "limit": limit, "fields": FIELDS},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])

    papers = []
    for item in data:
        ext_ids = item.get("externalIds") or {}
        papers.append(
            Paper(
                title=item.get("title") or "",
                source="semantic_scholar",
                source_id=item.get("paperId") or "",
                doi=ext_ids.get("DOI"),
                authors=[a.get("name", "") for a in (item.get("authors") or []) if isinstance(a, dict)],
                pub_date=item.get("publicationDate"),
                abstract=item.get("abstract"),
                url=item.get("url"),
            )
        )
    return papers
