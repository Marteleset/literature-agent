"""Apply transparent heuristic scores and generate a screening report.

Usage:
    python scripts/score_papers.py
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "processed" / "metadata.csv"
SCORED_CSV_PATH = ROOT / "data" / "processed" / "metadata_scored.csv"
REPORT_PATH = ROOT / "reports" / "latest_candidates.md"

POSITIVE_RULES = [
    (3, ["fault location", "fault locating", "fault diagnosis"]),
    (3, ["distribution network", "distribution system", "active distribution network", "adn"]),
    (2, ["distributed generation", "dg", "inverter", "renewable"]),
    (2, ["sparse measurement", "hybrid measurement", "pmu", "ftu", "phasor measurement"]),
    (2, ["missing data", "data loss", "packet loss", "incomplete measurement"]),
    (2, ["bad data", "outlier", "corrupted", "anomaly", "gross error"]),
    (2, ["sparse bayesian learning", "compressed sensing", "sparse recovery"]),
]

NEGATIVE_RULES = [
    (-3, ["transmission system state estimation"]),
    (-3, ["medical imaging", "image reconstruction", "magnetic resonance"]),
    (-2, ["cyber attack", "false data injection"]),
]


def score_text(text: str) -> tuple[int, list[str]]:
    lowered = text.lower()
    score = 0
    reasons: list[str] = []
    for points, phrases in POSITIVE_RULES + NEGATIVE_RULES:
        for phrase in phrases:
            if phrase in lowered:
                score += points
                reasons.append(f"{points:+d}: {phrase}")
                break
    return score, reasons


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Run search_openalex.py first: {CSV_PATH} does not exist")

    rows: list[dict[str, str]] = []
    with CSV_PATH.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            text = " ".join([
                row.get("title", ""),
                row.get("abstract", ""),
                row.get("concepts", ""),
            ])
            score, reasons = score_text(text)
            row["score"] = str(score)
            row["score_reasons"] = "; ".join(reasons)
            rows.append(row)

    rows.sort(key=lambda r: (int(r.get("score", 0)), int(r.get("year") or 0), int(r.get("cited_by_count") or 0)), reverse=True)

    fieldnames = list(rows[0].keys()) if rows else []
    with SCORED_CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as report:
        report.write("# Latest Literature Candidates\n\n")
        report.write("This report is generated from OpenAlex metadata and rough heuristic scores. It is intended for screening, not final judgment.\n\n")
        report.write("## Top candidates\n\n")
        for i, row in enumerate(rows[:30], start=1):
            report.write(f"### {i}. {row.get('title', '').strip()}\n\n")
            report.write(f"- Year: {row.get('year', '')}\n")
            report.write(f"- Venue: {row.get('venue', '')}\n")
            report.write(f"- DOI: {row.get('doi', '')}\n")
            report.write(f"- URL: {row.get('url', '')}\n")
            report.write(f"- Score: {row.get('score', '')}\n")
            report.write(f"- Reasons: {row.get('score_reasons', '')}\n")
            abstract = row.get("abstract", "")
            if len(abstract) > 900:
                abstract = abstract[:900] + "..."
            report.write(f"- Abstract: {abstract}\n\n")

    print(f"Saved scored metadata to {SCORED_CSV_PATH}")
    print(f"Saved report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
