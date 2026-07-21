import requests
from normalize import Paper, reconstruct_openalex_abstract
from config import CONTACT_EMAIL

BASE_URL = "https://api.openalex.org/works"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    params = {"search": query, "per-page": limit}
    if CONTACT_EMAIL:
        params["mailto"] = CONTACT_EMAIL  # puts you in OpenAlex's faster "polite pool"

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    papers = []
    for item in results:
        doi = item.get("doi")
        if doi:
            doi = doi.replace("https://doi.org/", "")

        authors = [
            (a.get("author") or {}).get("display_name", "")
            for a in item.get("authorships", [])
        ]

        raw_id = item.get("id") or ""
        source_id = raw_id.replace("https://openalex.org/", "")

        papers.append(
            Paper(
                title=item.get("title") or item.get("display_name") or "",
                source="openalex",
                source_id=source_id,
                doi=doi,
                authors=authors,
                pub_date=item.get("publication_date"),
                abstract=reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
                url=raw_id or None,
            )
        )
    return papers
