import requests
import xml.etree.ElementTree as ET
from normalize import Paper

BASE_URL = "http://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch(query: str, limit: int = 25) -> list[Paper]:
    resp = requests.get(
        BASE_URL,
        params={
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
        },
        timeout=30,
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    papers = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        arxiv_id = (entry.findtext(f"{ATOM_NS}id") or "").split("/abs/")[-1]
        title = (entry.findtext(f"{ATOM_NS}title") or "").strip().replace("\n", " ")
        summary = (entry.findtext(f"{ATOM_NS}summary") or "").strip().replace("\n", " ")
        published = entry.findtext(f"{ATOM_NS}published")  # e.g. 2023-05-01T00:00:00Z
        pub_date = published[:10] if published else None
        authors = [
            (a.findtext(f"{ATOM_NS}name") or "").strip()
            for a in entry.findall(f"{ATOM_NS}author")
        ]

        # arXiv preprints usually don't have a DOI; some do if later published.
        doi = entry.findtext("{http://arxiv.org/schemas/atom}doi")

        papers.append(
            Paper(
                title=title,
                source="arxiv",
                source_id=arxiv_id,
                doi=doi,
                authors=authors,
                pub_date=pub_date,
                abstract=summary,
                url=f"https://arxiv.org/abs/{arxiv_id}",
            )
        )
    return papers
