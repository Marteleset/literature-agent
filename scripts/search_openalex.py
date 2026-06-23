#!/usr/bin/env python3
"""Search OpenAlex and write normalized literature metadata.

Usage:
    python scripts/search_openalex.py
    python scripts/search_openalex.py --config config/queries.yaml --out data/processed
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import yaml

OPENALEX_WORKS_URL = "https://api.openalex.org/works"

CSV_FIELDS = [
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
    "query_topic",
    "query_text",
    "score",
    "reason_for_inclusion",
    "uncertainty",
]


def reconstruct_abstract(inv_index: dict[str, list[int]] | None) -> str:
    if not inv_index:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv_index.items():
        for idx in idxs:
            positions.append((idx, word))
    return " ".join(word for _, word in sorted(positions))


def fetch_openalex(query: str, year_from: int, per_page: int, sort: str) -> list[dict[str, Any]]:
    params = {
        "search": query,
        "filter": f"from_publication_date:{year_from}-01-01",
        "per-page": per_page,
        "sort": sort,
    }
    response = requests.get(OPENALEX_WORKS_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])


def normalize_work(work: dict[str, Any], topic: str, query: str) -> dict[str, Any]:
    authorships = work.get("authorships") or []
    authors = "; ".join(
        a.get("author", {}).get("display_name", "") for a in authorships if a.get("author")
    )
    venue = (work.get("primary_location") or {}).get("source", {}) or {}
    doi = work.get("doi") or ""
    concepts = "; ".join(
        c.get("display_name", "") for c in (work.get("concepts") or [])[:8]
    )
    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))

    row = {
        "paper_id": (work.get("id") or "").rsplit("/", 1)[-1],
        "title": work.get("title") or "",
        "year": work.get("publication_year") or "",
        "authors": authors,
        "venue": venue.get("display_name", ""),
        "doi": doi,
        "openalex_id": work.get("id") or "",
        "url": doi or work.get("id") or "",
        "abstract": abstract,
        "concepts": concepts,
        "query_topic": topic,
        "query_text": query,
        "score": "",
        "reason_for_inclusion": "",
        "uncertainty": "not_screened",
    }
    return row


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for row in rows:
        key = (row.get("doi") or row.get("openalex_id") or row.get("title") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "metadata.csv"
    jsonl_path = out_dir / "metadata.jsonl"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/queries.yaml")
    parser.add_argument("--out", default="data/processed")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    settings = config.get("settings", {})
    year_from = int(settings.get("from_publication_year", 2015))
    per_query_limit = int(settings.get("per_query_limit", 25))
    sort = settings.get("sort", "relevance_score:desc")

    rows: list[dict[str, Any]] = []
    for topic in config.get("topics", []):
        topic_name = topic["name"]
        for query in topic.get("queries", []):
            print(f"Searching [{topic_name}] {query}")
            works = fetch_openalex(query, year_from, per_query_limit, sort)
            rows.extend(normalize_work(work, topic_name, query) for work in works)
            time.sleep(0.2)

    rows = dedupe_rows(rows)
    write_outputs(rows, Path(args.out))
    print(f"Wrote {len(rows)} unique records to {args.out}")


if __name__ == "__main__":
    main()
