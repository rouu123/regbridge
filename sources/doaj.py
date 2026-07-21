import requests
from urllib.parse import quote
from normalize import Paper

BASE_URL = "https://doaj.org/api/search/articles"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    resp = requests.get(
        f"{BASE_URL}/{quote(query)}",
        params={"pageSize": limit},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    papers = []
    for item in results:
        bibjson = item.get("bibjson", {})
        doi = None
        for ident in bibjson.get("identifier", []):
            if ident.get("type", "").lower() == "doi":
                doi = ident.get("id")
                break

        year = bibjson.get("year")
        month = bibjson.get("month")
        pub_date = None
        if year:
            pub_date = f"{year}-{int(month):02d}" if month else str(year)

        papers.append(
            Paper(
                title=bibjson.get("title") or "",
                source="doaj",
                source_id=item.get("id", ""),
                doi=doi,
                authors=[a.get("name", "") for a in bibjson.get("author", [])],
                pub_date=pub_date,
                abstract=bibjson.get("abstract"),
                url=next(
                    (l.get("url") for l in bibjson.get("link", []) if l.get("url")),
                    None,
                ),
            )
        )
    return papers
