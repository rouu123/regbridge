import requests
from urllib.parse import quote
from normalize import Paper

BASE_URL = "https://doaj.org/api/search/articles"


MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def _parse_pub_date(year: object, month: object) -> str | None:
    if not year:
        return None
    if not month:
        return str(year)
    try:
        m_int = int(month)
        if 1 <= m_int <= 12:
            return f"{year}-{m_int:02d}"
    except (ValueError, TypeError):
        pass

    if isinstance(month, str):
        m_str = month.strip().lower()
        if m_str in MONTH_MAP:
            return f"{year}-{MONTH_MAP[m_str]:02d}"

    return str(year)


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

        pub_date = _parse_pub_date(bibjson.get("year"), bibjson.get("month"))

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
