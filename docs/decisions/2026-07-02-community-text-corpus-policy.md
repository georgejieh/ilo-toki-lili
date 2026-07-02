# Community Text Corpus Policy

## Status

Accepted.

## Decision

Third-party and community Toki Pona text used for the non-synthetic corpus is local-only by default. The public repository may track source manifests, URLs or source git commits, author metadata, license/provenance metadata, retrieval and filtering code, checksums, word counts, attribution files, and aggregate statistics. It should not track raw scraped text, near-verbatim corpus dumps, or redistributed article, zine, post, or wiki content.

Public dataset releases may include non-synthetic T4 items only when each item has a verified compatible license and per-item attribution.

## Rationale

The project needs grounded text, not just synthetic grammar strings. Community sources such as Tatoeba Toki Pona, lipu tenpo, poki Lapo, utala pona, and sona.pona.la are valuable because they contain lived Toki Pona usage connected to context, topics, art, games, and public activity.

Those same sources can carry copyright and license obligations. As of the v2.8 master plan, Tatoeba Toki Pona is treated as CC-BY; lipu tenpo is treated as blanket CC BY-SA 4.0; poki Lapo is treated as a source repository with per-file license metadata and `lipu.pona.la` as its presentation frontend; utala pona submissions are treated as CC BY-SA 4.0 and contest rules ban AI-generated text; sona.pona.la must be checked at ingest. Training on retrieved text and publishing verbatim copies of retrieved text are different release surfaces, so the repository keeps the conservative boundary: recreate locally, do not redistribute raw community text through the repo.

This is project hygiene rather than legal advice. When a future release needs to publish examples or a derived dataset, review the source-specific license terms first.

## Consequences

- T4 and other non-synthetic ingestion jobs write raw text to ignored local paths.
- Ingestion metadata preserves per-item source URL or git commit, author, license signal, checksum, word count, retrieval time, and transformation notes.
- Unknown or ambiguous licenses are skipped or isolated for manual review.
- Public artifacts prefer reproducible recipes, hashes, counts, attribution files, and evaluation summaries over raw text.
- Synthetic and project-authored data can still be committed when it has no third-party redistribution issue.
