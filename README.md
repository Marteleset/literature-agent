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
2. Run `scripts/search_openalex.py` to collect raw and processed metadata.
3. Run `scripts/score_papers.py` to add rough relevance labels.
4. Review `reports/latest_candidates.md` with ChatGPT.
5. Revise the search queries and repeat.

## Research seed

The initial target is fault location in active distribution networks under sparse, missing, and corrupted measurements, especially with DG, PMU/FTU hybrid measurements, sparse Bayesian learning, and compressed sensing.
