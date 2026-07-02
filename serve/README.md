# Serve

The serving layer will expose the trained models and scene renderer through a small FastAPI service.

Planned endpoints include random held-out scenes, rendering, generation, forced choice, and surprise traces for anomaly examples.

If arena feedback endpoints are added, their data is post-publication follow-up material only. Arena logs must not enter v1 training data or frozen evaluation evidence.

If a standalone `toki-sona` assistant is added after the comparison, serve it as a separate product surface from the frozen A/B/C demo. Candidate capabilities include longer reasoning passes, council-style self-comparison, and RAG over a pre-vetted Toki Pona-only source index with visible provenance. It should not use account-specific memory unless a later privacy decision explicitly adds accounts and retention rules.
