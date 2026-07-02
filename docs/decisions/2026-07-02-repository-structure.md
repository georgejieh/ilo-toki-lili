# Repository Structure

Date: 2026-07-02

Decision: organize the project around the research pipeline: `configs/`, `data/`, `models/`, `train/`, `eval/`, `serve/`, `web/`, `infra/`, `docs/`, and `tests/`.

Rationale: the project has both research and product deliverables. Keeping data generation, training, evaluation, serving, and frontend code in separate top-level areas makes cross-stage contracts visible and keeps the final demo from becoming an afterthought.

Consequence: tests mirror the source tree, config keys are treated as run contracts, and large datasets or generated artifacts stay outside version control unless a deliberate release process says otherwise.
