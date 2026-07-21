# Research paper metadata scraper

Pulls title / DOI / authors / date / abstract from multiple sources and
stores everything in Qdrant: metadata as payload fields, abstract text also
as a payload field, and the embedding vector for semantic search — all on
one point, so there's nothing separate to link.

## Sources implemented

| Source | API key needed? | Notes |
|---|---|---|
| Semantic Scholar | optional (higher rate limit with one) | |
| arXiv | no | Atom/XML API, most preprints have no DOI |
| OpenAlex | no (add your email for the "polite pool") | abstracts come back as an inverted index; we reconstruct plain text |
| CORE | **yes**, free at core.ac.uk/services/api | |
| Springer Nature | **yes**, free at dev.springernature.com | Meta API v2 |
| DOAJ | no | open-access journals only |

## Sources NOT implemented, and why

- **Papers With Code** — Meta shut it down in July 2025; the domain now
  redirects to Hugging Face Trending Papers. There's no API left to call.
- **BASE (Bielefeld)** — their OAI-PMH interface is IP-restricted. You have
  to apply to Bielefeld University Library as a registered non-commercial
  project before they'll let a server query it.
- **ScienceOpen** — no public API for research articles/preprints (only an
  OAI-PMH feed for their separate BookMetaHub book/chapter metadata project).
  Scraping their search HTML is fragile and likely against their terms —
  skipped rather than faked.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
```

Qdrant collection is created automatically on first run (`BAAI/bge-m3` via
`sentence-transformers` outputs 1024-dim vectors, configured in `store.py`;
the model weights (~2GB) download once on first run and are cached locally).

## Usage

Edit `QUERY`, `LIMIT_PER_SOURCE`, or comment out sources you don't have keys
for at the top of `main.py`, then:

```bash
python main.py
```

Re-running with the same query is safe — `store.py` checks by DOI (or
source+source_id when there's no DOI) via a Qdrant payload filter before
writing, so you get an update-in-place rather than a duplicate point.

## How it fits together

1. Each source module (`sources/*.py`) returns a list of `Paper` objects with
   a consistent shape (see `normalize.py`).
2. `main.py` deduplicates across sources (by DOI when available).
3. Every paper gets embedded — its abstract if it has one, otherwise its
   title, so nothing is silently dropped for lack of an abstract.
4. `store.py` upserts one Qdrant point per paper: `vector` = the embedding,
   `payload` = title, DOI, authors, date, source, url, and the abstract text
   itself. Retrieval for RAG is a single call: query Qdrant, get back
   `payload.abstract` (and everything else) directly on each hit — no second
   database round-trip needed.

## Scraped vs. manually-added papers

Every `Paper` has an `origin` field: `"scraped"` by default (set automatically
for anything that comes out of `sources/*.py`), or `"user_upload"` for papers
you add by hand. It's stored as a normal Qdrant payload field, so you can
filter on it in a query (e.g. only show `origin == "user_upload"` results,
or exclude them from a scrape re-run).

To add one manually:

```bash
python add_manual.py
```

Edit the `add_paper(...)` call at the bottom of `add_manual.py` with the
real title/abstract/DOI/authors, or import `add_paper()` from your own
script/notebook.

## If you ever want SQL back

If you later want exact filtering, joins, or reporting that goes beyond
Qdrant's payload filters, the metadata fields are already sitting there as a
flat dict per paper (see `Paper` in `normalize.py`) — reintroducing a
Postgres/Supabase table would just mean writing that same dict to a second
place in `store.py`, same as the original two-store version of this project.
