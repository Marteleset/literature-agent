#!/usr/bin/env python3
"""Apply simple keyword-based screening scores to OpenAlex metadata.

This script is intentionally heuristic. It should help prioritize papers for
human/ChatGPT screening, not decide research value automatically.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

POSITIVE_RULES = [
    (3, ["fault location"]),
    (3, ["distribution network"]),
    (3, ["active distribution network"]),
    (2, ["distributed generation", "inverter", "renewable"]),
    (2, ["sparse measurement", "hybrid measurement", "pmu", "ftu"]),
    (2, ["missing data", "data loss", "packet loss"]),
    (2, ["bad data", "outlier", "corrupted", "anomaly"]),
    (2, ["sparse bayesian learning", "compressed sensing"]),
]

NEGATIVE_RULES = [
    (-3, ["transmission system state estimation"]),
    (-3, ["image reconstruction", "medical imaging", "magnetic resonance imaging"]),
    (-2, ["cyberattack", "false data injection attack"]),
]


def score_text(text: str) -> tuple[int, list[str]]:
    text_l = text.lower()
    score = 0
    reasons: list[str] = []
    for points, terms in POSITIVE_RULES + NEGATIVE_RULES:
        matched = [term for term in terms if term in text_l]
        if matched:
            score += points
            reasons.append(f"{points:+d}: {', '.join(matched)}")
    return score, reasons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/metadata.csv")
    parser.add_argument("--output", default="data/processed/metadata_scored.csv")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    for field in ["score", "reason_for_inclusion", "uncertainty"]:
        if field not in fieldnames:
            fieldnames.append(field)

    for row in rows:
        text = " ".join([
            row.get("title", ""),
            row.get("abstract", ""),
            row.get("concepts", ""),
            row.get("query_text", ""),
        ])
        score, reasons = score_text(text)
        row["score"] = str(score)
        row["reason_for_inclusion"] = " | ".join(reasons)
        row["uncertainty"] = "heuristic_only"

    rows.sort(key=lambda r: int(r.get("score") or 0), reverse=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote scored metadata to {output_path}")


if __name__ == "__main__":
    main()
