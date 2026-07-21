import requests
from normalize import Paper
from config import CORE_API_KEY

BASE_URL = "https://api.core.ac.uk/v3/search/works"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    if not CORE_API_KEY:
        raise RuntimeError("CORE_API_KEY is not set (get a free key at core.ac.uk/services/api)")

    resp = None
    for attempt in range(2):
        try:
            resp = requests.post(
                BASE_URL,
                headers={"Authorization": f"Bearer {CORE_API_KEY}"},
                json={"q": query, "limit": limit},
                timeout=45,
            )
            resp.raise_for_status()
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == 0:
                continue
            raise
    results = (resp.json() if resp else {}).get("results", [])

    papers = []
    for item in results:
        authors = [a.get("name", "") for a in (item.get("authors") or [])]
        source_urls = item.get("sourceFulltextUrls") or []
        year_pub = item.get("yearPublished")
        pub_date = item.get("publishedDate") or (str(year_pub) if year_pub is not None else None)
        papers.append(
            Paper(
                title=item.get("title") or "",
                source="core",
                source_id=str(item.get("id", "")),
                doi=item.get("doi"),
                authors=authors,
                pub_date=pub_date,
                abstract=item.get("abstract"),
                url=item.get("downloadUrl") or (source_urls[0] if source_urls else None),
            )
        )
    return papers
