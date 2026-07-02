# Webapp Resource And Toki Sona Surface

## Status

Accepted as future product scope.

## Decision

The public web app should eventually include more than the controlled A/B/C comparison. It should also provide Toki Pona background material, authoritative links, learning resources, corpus-source context, and source/license notes so visitors can understand the language and the project without leaving the page immediately.

If `toki-sona` is strong enough after the frozen comparison, the project may add a separate standalone `toki-sona` assistant surface. This surface can be optimized for usefulness and delight in ways the comparison models cannot: longer reasoning passes, council-style multiple generations, retrieval over a curated Toki Pona-only source index, source citations, and polished chat ergonomics. It is a product/demo layer, not headline evidence for the research claim.

## Boundary

- The research comparison remains clean: A, B, and C are evaluated from frozen artifacts and matched rules.
- The standalone `toki-sona` assistant must be labeled separately from the A/B/C comparison.
- Wrapper features do not retroactively change evaluation results.
- Retrieval uses a pre-vetted source list. Model-visible retrieved text should be Toki Pona-only unless a later decision explicitly approves a different source type.
- No account-specific memory is planned for the first version. Adding memory requires a later privacy and retention decision.
- Arena votes and assistant logs remain post-publication follow-up material and do not enter v1 training or frozen evaluation evidence.

## Initial Resource Set

The first resource page should curate links rather than generate them dynamically. Initial candidates:

- `tokipona.org`: official site, books, FAQ, and creator-linked material.
- `tokipona.net`: community hub with learning links, communities, literature, tools, and media.
- `sona.pona.la`: Toki Pona wiki and resource index.
- Linku or `nimi.li`: dictionary and word-usage reference.
- T4 source family from the corpus policy: Tatoeba Toki Pona, lipu tenpo, poki Lapo or `lipu.pona.la`, utala pona, and any later admitted source with license/provenance notes.

## Consequences

- Phase 10 needs information architecture for a resource page, the controlled comparison, and the optional `toki-sona` assistant.
- Serving code should keep frozen comparison endpoints separate from product-assistant endpoints.
- Any RAG/deep-research feature needs a source registry, provenance display, and tests that prevent unapproved open-web retrieval.
- The README and web docs can mention the assistant as optional future scope, but not as a guaranteed result.
