"""Search OpenAlex and export normalized literature metadata.

Usage:
    python scripts/search_openalex.py

Outputs:
    data/raw/openalex_results.jsonl
    data/processed/metadata.csv
    data/processed/metadata.jsonl
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "queries.yaml"
RAW_PATH = ROOT / "data" / "raw" / "openalex_results.jsonl"
CSV_PATH = ROOT / "data" / "processed" / "metadata.csv"
JSONL_PATH = ROOT / "data" / "processed" / "metadata.jsonl"
OPENALEX_URL = "https://api.openalex.org/works"

FIELDS = [
    "paper_id",
    "title",
    "year",
    "authors",
    "venue",
    "doi",
    "openalex_id",
    "url",
    "abstract",
    "concepts",
    "cited_by_count",
    "is_open_access",
    "pdf_url",
    "source_topic",
    "source_query",
]


def abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(word for _, word in sorted(words))


def normalize_work(work: dict[str, Any], topic_name: str, query: str) -> dict[str, Any]:
    authorships = work.get("authorships") or []
    authors = "; ".join(
        a.get("author", {}).get("display_name", "")
        for a in authorships
        if a.get("author", {}).get("display_name")
    )
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    open_access = work.get("open_access") or {}
    concepts = work.get("concepts") or []

    return {
        "paper_id": (work.get("id") or "").rsplit("/", 1)[-1],
        "title": work.get("title") or "",
        "year": work.get("publication_year") or "",
        "authors": authors,
        "venue": source.get("display_name") or "",
        "doi": work.get("doi") or "",
        "openalex_id": work.get("id") or "",
        "url": work.get("landing_page_url") or work.get("id") or "",
        "abstract": abstract_from_inverted_index(work.get("abstract_inverted_index")),
        "concepts": "; ".join(c.get("display_name", "") for c in concepts[:8]),
        "cited_by_count": work.get("cited_by_count") or 0,
        "is_open_access": open_access.get("is_oa", False),
        "pdf_url": open_access.get("oa_url") or "",
        "source_topic": topic_name,
        "source_query": query,
    }


def search_openalex(query: str, per_page: int, from_year: int, mailto: str = "") -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "search": query,
        "per-page": per_page,
        "filter": f"from_publication_date:{from_year}-01-01",
        "sort": "relevance_score:desc",
    }
    if mailto:
        params["mailto"] = mailto
    response = requests.get(OPENALEX_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])


def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    settings = config.get("settings", {})
    per_query = int(settings.get("per_query", 25))
    from_year = int(settings.get("from_publication_year", 2015))
    mailto = settings.get("mailto", "")

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    rows: list[dict[str, Any]] = []

    with RAW_PATH.open("w", encoding="utf-8") as raw_file:
        for topic in config.get("topics", []):
            topic_name = topic.get("name", "unnamed_topic")
            for query in topic.get("queries", []):
                print(f"Searching [{topic_name}] {query}")
                works = search_openalex(query, per_query, from_year, mailto)
                for work in works:
                    raw_file.write(json.dumps({"topic": topic_name, "query": query, "work": work}, ensure_ascii=False) + "\n")
                    row = normalize_work(work, topic_name, query)
                    key = row["doi"] or row["openalex_id"] or row["title"].lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(row)
                time.sleep(0.2)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with JSONL_PATH.open("w", encoding="utf-8") as jsonl_file:
        for row in rows:
            jsonl_file.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved {len(rows)} unique records to {CSV_PATH}")


if __name__ == "__main__":
    main()
