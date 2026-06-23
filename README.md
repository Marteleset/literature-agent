# literature-agent

A lightweight literature-search workspace for iterative research screening.

This repository is designed as a shared handoff space between Codex-style execution and ChatGPT-style research reasoning.

## First milestone

The first version should do four things:

1. Search OpenAlex with topic-specific queries.
2. Normalize paper metadata into CSV and JSONL files.
3. Apply transparent heuristic scores for rough screening.
4. Generate a Markdown candidate report for human review.

## Intended workflow

1. Edit `config/queries.yaml` to describe the research direction.
2. Run `python scripts/search_openalex.py` to collect raw and processed metadata.
3. Run `python scripts/score_papers.py` to add rough relevance labels and create a report.
4. Review `reports/latest_candidates.md` with ChatGPT.
5. Revise the search queries and repeat.

## Research seed

The initial target is fault location in active distribution networks under sparse, missing, and corrupted measurements, especially with DG, PMU/FTU hybrid measurements, sparse Bayesian learning, and compressed sensing.

## Notes for Codex

Keep the pipeline simple and auditable. Prefer structured metadata and clear logs over long natural-language summaries. Do not download PDFs in the first stage unless a later screening request explicitly asks for full-text extraction.
