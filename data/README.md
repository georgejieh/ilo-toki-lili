# Data

This directory owns the dataset contract: vocabulary, schemas, tokenizer, grammar, synthetic world generation, review material, and shard-writing code.

Tracked files here should be small, auditable, and reproducible. Large or license-sensitive inputs stay local under ignored directories such as `raw/`, `external/`, `community/`, `non_synthetic/`, `third_party/`, `interim/`, `processed/`, `shards/`, `tiers/corpus_t4/`, `tiers/t4_raw/`, and `tiers/t4_processed/`.

Community and other non-synthetic text is local-only by default. Public commits should include source lists, retrieval code, license/provenance notes, attribution files, filtering rules, aggregate statistics, and reproducibility hashes, but not verbatim scraped articles, zines, competition entries, wiki pages, or corpus dumps.

T4 ingestion should preserve per-item source URL or git commit, author when known, license signal, checksum, word count, retrieval time, and transformation notes. Prefer source repositories with item-level metadata, such as poki Lapo, over scraping presentation frontends such as `lipu.pona.la`.

Planned modules:

- `VOCAB_SOURCE.md`: Linku source, acquisition, license, and attribution policy for vocabulary artifacts.
- `vocab.json`: the frozen 137-word vocabulary plus special tokens.
- `holdouts.json`: locked compositional holdout registry.
- `schemas.py`: pydantic models shared by data generation, training, eval, and serving.
- `tokenizer.py`: closed-vocabulary word tokenizer.
- `grammar/`: Toki Pona grammar, description generation, parsing, and style filters.
- `world/`: scene sampling, rendering, physics, sprites, and diversity audits.
- `tiers/`: dataset tier generators and shard writer.
- `review/`: human review prompts, verdicts, and release notes.
