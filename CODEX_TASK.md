# Codex Task: First Literature Search Agent

Goal: keep this repository as a small, auditable literature-search pipeline.

## Immediate task

1. Install dependencies from `requirements.txt`.
2. Run `python scripts/search_openalex.py`.
3. Run `python scripts/score_papers.py`.
4. Check whether the generated `reports/latest_candidates.md` is readable.
5. Commit generated outputs only if they are not too large.

## Important constraints

- Do not download PDFs in the first stage.
- Do not replace structured metadata with long prose summaries.
- Keep DOI, OpenAlex ID, source query, and URL for traceability.
- If a result looks relevant but uncertain, preserve it and mark the uncertainty rather than deleting it.

## Future improvements

- Add better deduplication by DOI and title similarity.
- Add support for Crossref or Semantic Scholar.
- Add a second-stage PDF metadata collector for papers selected by ChatGPT.
- Add topic-specific negative filters after the first screening round.
