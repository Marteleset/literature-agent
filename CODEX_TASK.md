# Codex Task Guide

Use this repository as a small literature discovery pipeline.

## First task

Run the initial OpenAlex search and scoring pipeline.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/search_openalex.py
python scripts/score_papers.py
```

Then inspect `data/processed/metadata_scored.csv` and update `reports/latest_candidates.md` with the top candidates.

## Expected output

The report should not be a long literature review. It should be a screening handoff for ChatGPT, with:

- top 20 to 30 candidate papers;
- title, year, venue, DOI or URL;
- score and reason for inclusion;
- short uncertainty notes;
- a next-search question list.

## Important boundary

Do not crawl full PDFs in the first round. Only use metadata, abstracts, concepts, DOI, and open-access links from OpenAlex.

After ChatGPT screens the candidates, use the selected list to perform targeted full-text retrieval in a later round.
