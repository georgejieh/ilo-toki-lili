# Vocabulary Source

Date: 2026-07-02

Status: accepted for Phase 0 source acquisition. The exact `data/vocab.json` contents and partition tags are frozen separately in the Phase 0 vocabulary decision.

## Canonical Upstream

The Phase 0 vocabulary generator uses Linku's `sona` dataset as its canonical upstream:

- Project: `lipu-linku/sona`
- Repository: <https://github.com/lipu-linku/sona>
- Word data directory: <https://github.com/lipu-linku/sona/tree/main/words>
- License: CC-BY-SA-4.0

Use `sona` as the source data repository, not the Linku web app repository. The web dictionary is a presentation surface; `sona` is the dataset that backs Linku word metadata, definitions, and packaged API data.

## Acquisition Path

For the draft vocabulary generator:

1. Pin a specific upstream `lipu-linku/sona` commit or release tag before reading any files.
2. Read word metadata from `words/` and its subdirectories.
3. Prefer the source TOML files over generated API JSON when the same information is available in both places.
4. Use `api/raw/v2` only as a convenience mirror when it can be tied back to the same pinned upstream commit.
5. Write a source manifest next to generated vocabulary artifacts.

The source manifest must include:

- upstream repository URL
- upstream commit SHA or release tag
- retrieval date
- upstream license
- exact upstream files used
- SHA256 checksums of copied source snapshots or fetched generated JSON
- local generator command or module
- local project commit SHA that generated the artifact

## Scope For Model-Visible Data

The project vocabulary target remains the 137-word closed vocabulary from the master plan: 120 `nimi pu` plus 17 `nimi ku suli`. Linku is the arbiter for community usage semantics, especially where visual categories or ordinary usage boundaries matter.

English definitions, commentary, etymology, and translation fields are allowed only as human-audit metadata for choosing and reviewing vocabulary entries. They must not enter model-visible training, evaluation, tokenizer fixtures, shard text, or prompts. Model-visible text stays limited to frozen Toki Pona words, punctuation, and special tokens.

## License Handling

`sona Linku` is licensed under CC-BY-SA-4.0. Any committed or released vocabulary artifact derived from it must preserve attribution and carry compatible share-alike terms where the derived artifact is redistributed.

The repository may commit:

- the generated project vocabulary
- source manifests
- license and attribution notes
- checksums and reproducibility metadata
- extraction code

Avoid committing bulky raw upstream snapshots unless a later release decision says the redistributed form is needed. If raw snapshots are kept locally during generation, place them under ignored data directories.

## Non-Goals

- Do not scrape `linku.la` or `nimi.li` pages for the Phase 0 source snapshot.
- Do not treat the Linku web app license as the dataset license.
- Do not mix third-party corpus text policy with vocabulary metadata; community text ingestion has its own provenance and redistribution rules.
