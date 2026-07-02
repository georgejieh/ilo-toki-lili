# Community Text Corpus Policy

## Status

Accepted.

## Decision

Third-party and community Toki Pona text used for the non-synthetic corpus is local-only by default. The public repository may track source manifests, URLs, license/provenance metadata, retrieval and filtering code, checksums, and aggregate statistics. It should not track raw scraped text, near-verbatim corpus dumps, or redistributed article, zine, post, or wiki content unless a deliberate release review clears the exact material.

## Rationale

The project needs grounded text, not just synthetic grammar strings. Community sources such as lipu tenpo, utala pona, and lipu Linku (`lipu.pona.la`) are valuable because they contain lived Toki Pona usage connected to context, topics, art, games, and public activity.

Those same sources can carry copyright and license obligations. As of the repository setup, lipu tenpo describes its issues, images, and entries as CC BY-SA 4.0; utala pona describes submissions as CC BY-SA 4.0; lipu Linku (`lipu.pona.la`) notes that article licenses are specified individually while the site source code is GPL-3.0. Training on retrieved text and publishing verbatim copies of retrieved text are different release surfaces, so the repository keeps the conservative boundary: recreate locally, do not redistribute raw community text by default.

This is project hygiene rather than legal advice. When a future release needs to publish examples or a derived dataset, review the source-specific license terms first.

## Consequences

- T4 and other non-synthetic ingestion jobs write raw text to ignored local paths.
- Ingestion metadata preserves per-source URL, retrieval time, license signal, and transformation notes.
- Unknown or ambiguous licenses are skipped or isolated for manual review.
- Public artifacts prefer reproducible recipes, hashes, counts, and evaluation summaries over raw text.
- Synthetic and project-authored data can still be committed when it has no third-party redistribution issue.
