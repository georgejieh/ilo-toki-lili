# Data

This directory owns the dataset contract: vocabulary, schemas, tokenizer, grammar, synthetic world generation, review material, and shard-writing code.

Tracked files here should be small, auditable, and reproducible. Large or license-sensitive inputs stay local under ignored directories such as `raw/`, `external/`, `interim/`, `processed/`, and `shards/`.

Planned modules:

- `vocab.json`: the frozen 137-word vocabulary plus special tokens.
- `holdouts.json`: locked compositional holdout registry.
- `schemas.py`: pydantic models shared by data generation, training, eval, and serving.
- `tokenizer.py`: closed-vocabulary word tokenizer.
- `grammar/`: Toki Pona grammar, description generation, parsing, and style filters.
- `world/`: scene sampling, rendering, physics, sprites, and diversity audits.
- `tiers/`: dataset tier generators and shard writer.
- `review/`: human review prompts, verdicts, and release notes.
