# Web

The public demo app will let people compare the three models side by side.

Design direction: calm, minimal, and research-forward. The interface should make scoped claims, explain why Toki Pona is a pragmatic testbed, and avoid turning exploratory arena feedback into headline evidence.

The site has three future-facing surfaces:

- Toki Pona context: background, authoritative links, learning resources, corpus-source bibliography, and source/license notes.
- Research demo: held-out scene composer, A/B/C side-by-side comparison, results explorer, and blind arena.
- Standalone `toki-sona`: only if Model C earns it, a separate Toki Pona-only assistant experience optimized for usefulness rather than clean experimental comparison.

Planned views:

- Toki Pona background and learning guide
- source bibliography and corpus provenance page
- scene composer
- model playground
- side-by-side comparison
- bootstrapped vocabulary demo
- anomaly player
- paper figures explorer
- sitelen pona display toggle
- blind arena feedback
- standalone `toki-sona` assistant

Arena mode should randomize model labels, disclose anonymous feedback logging, and keep votes or flags firewalled from v1 training and frozen evaluation claims.

The sitelen pona toggle is display-only. It changes UI rendering for humans; model tokens stay word-level Latin text, and glyph images are not used as model input.

Initial source and learning links should be curated rather than generated on the fly. The first pass should include the official site at `tokipona.org`, the community hub at `tokipona.net`, `sona.pona.la`, Linku or `nimi.li`, and the corpus-source family used by the project such as lipu tenpo, utala pona, poki Lapo or `lipu.pona.la`, Tatoeba, and other sources admitted by the T4 provenance policy.

The standalone `toki-sona` surface is allowed to have wrapper features that the research comparison should not have: extended reasoning, multiple-pass council answers, retrieval over a pre-vetted Toki Pona-only source index, citation/provenance display, and deeper tool-like workflows. It should not require accounts for core use, and account-specific memory is out of scope unless a future privacy and product decision adds it. Any retrieval source shown to the model must be Toki Pona-only or otherwise explicitly approved; no open-web English research loop by default.
