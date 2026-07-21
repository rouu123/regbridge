from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Paper:
    title: str
    source: str          # 'semantic_scholar' | 'arxiv' | 'openalex' | 'core' | 'springer' | 'doaj'
    source_id: str        # native id within that source, used for de-duplication
    doi: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    pub_date: Optional[str] = None   # ISO 'YYYY-MM-DD' (or 'YYYY' / 'YYYY-MM' if that's all we get)
    abstract: Optional[str] = None
    url: Optional[str] = None
    origin: str = "scraped"  # 'scraped' (came from one of the source APIs) or 'user_upload'

    def dedupe_key(self) -> str:
        # Prefer DOI when present (it's the closest thing to a global paper id),
        # otherwise fall back to source+source_id.
        return self.doi.lower().strip() if self.doi else f"{self.source}:{self.source_id}"


def reconstruct_openalex_abstract(inverted_index: Optional[dict]) -> Optional[str]:
    """OpenAlex gives back abstracts as {word: [positions]} to dodge copyright
    issues with storing raw text. Rebuild the plain-text string from it."""
    if not inverted_index:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    if not positions:
        return None
    return " ".join(positions[i] for i in sorted(positions))
