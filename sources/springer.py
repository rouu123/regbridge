import requests
from normalize import Paper
from config import SPRINGER_API_KEY

BASE_URL = "https://api.springernature.com/meta/v2/json"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    if not SPRINGER_API_KEY:
        raise RuntimeError("SPRINGER_API_KEY is not set (get a free key at dev.springernature.com)")

    resp = requests.get(
        BASE_URL,
        params={"q": query, "api_key": SPRINGER_API_KEY, "p": limit},
        timeout=30,
    )
    resp.raise_for_status()
    records = resp.json().get("records", [])

    papers = []
    for item in records:
        authors = [c.get("creator", "") for c in (item.get("creators") or [])]
        urls = item.get("url")
        url_val = urls[0].get("value") if isinstance(urls, list) and len(urls) > 0 and isinstance(urls[0], dict) else None
        papers.append(
            Paper(
                title=item.get("title") or "",
                source="springer",
                source_id=item.get("identifier", "") or item.get("doi", "") or "",
                doi=item.get("doi"),
                authors=authors,
                pub_date=item.get("publicationDate"),
                abstract=item.get("abstract"),
                url=url_val,
            )
        )
    return papers
