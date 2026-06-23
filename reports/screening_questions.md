# Screening Questions for ChatGPT

After generating `latest_candidates.md`, ask ChatGPT to classify papers into the following groups:

1. Must read carefully.
2. Useful background only.
3. Possible overlap or competition.
4. Likely irrelevant despite matching keywords.
5. Worth expanding into a second-round search.

For the current research topic, pay special attention to:

- whether the paper truly addresses fault location, not only state estimation;
- whether DG/ADN is modeled explicitly;
- whether missing data and bad data are part of the method or only mentioned as motivation;
- whether sparse Bayesian learning, compressed sensing, or sparse recovery is central;
- whether the paper assumes dense PMU deployment that conflicts with sparse measurement conditions.
