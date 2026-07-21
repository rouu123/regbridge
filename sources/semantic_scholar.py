import time
import requests
from normalize import Paper
from config import SEMANTIC_SCHOLAR_API_KEY

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,externalIds,authors,abstract,publicationDate,url"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY

    resp = None
    for attempt in range(3):
        resp = requests.get(
            BASE_URL,
            params={"query": query, "limit": limit, "fields": FIELDS},
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 429 and attempt < 2:
            time.sleep(3 * (attempt + 1))
            continue
        resp.raise_for_status()
        break

    data = (resp.json() if resp else {}).get("data", [])

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
