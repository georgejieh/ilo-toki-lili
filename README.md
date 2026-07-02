# ilo toki lili

> sona suli li ken lon nimi lili.

ilo toki lili is a small language-modeling project for Toki Pona. The question is simple: when a model learns a tiny language, does it behave differently if the words are tied to a small world it can see?

Toki Pona is a good testbed because it makes every word work hard. Its vocabulary is small, its sounds are few, and its style rewards careful composition. That gives this project a pleasant constraint: build a world small enough to audit, then ask models to learn from it without hiding behind scale.

## The Bet

The project compares three matched small models:

| Codename | Model | Training signal | What it tests |
|---|---|---|---|
| `toki-taso` | decoder-only transformer | text only | the baseline |
| `toki-lukin` | transformer with visual prefix | text plus rendered scenes | grounding with a standard architecture |
| `toki-sona` | visual slots, recurrent world state, decoder | same grounded corpus | whether persistent state changes behavior |

All three models use the same Toki Pona vocabulary, the same text stream, roughly the same parameter budget, and the same capped room for tuning. The main evaluations are not about sounding fluent. They are about compositional generalization, contradiction detection, temporal reasoning, counterfactuals, robustness under visual domain shift, and whether a model can connect a word it has only read about to a visual concept later.

## How It Works

The repo is organized around an auditable research pipeline:

1. Build a closed Toki Pona vocabulary and tokenizer.
2. Generate a small visual world with scenes, entities, relations, and events.
3. Render paired image and text data from verified scene descriptions.
4. Lock holdout families before training.
5. Train the three model families from scratch.
6. Score them with forced-choice and parser-checked evaluations.
7. Release a web app where people can try the models side by side, including a blind arena for post-publication feedback.

The grounding world is intentionally modest: simple shapes, sprites, movement, containment, transfer, eating, falling, breaking. The point is not photorealism. The point is whether words like `soweli`, `insa`, `pana`, or `pakala` become more than text patterns when the training setup gives them a world to live in.

For community-written Toki Pona text, the repo keeps the map rather than the pile: source manifests, license notes, filters, hashes, and statistics are public, while raw third-party text stays local unless it is cleared for release.

## Repository Map

- `configs/`: experiment configs and ablation settings.
- `data/`: vocabulary, schemas, tokenizer, grammar, world generation, review notes, and local dataset documentation.
- `models/`: model architectures and parameter parity checks.
- `train/`: training loops, curriculum scheduling, data loading, and reinforcement-learning code.
- `eval/`: evaluation items, scoring, statistics, and report generation.
- `serve/`: FastAPI service for model inference and scene rendering.
- `web/`: public demo app.
- `infra/`: cloud training and sync helpers.
- `docs/`: research notes, project plan, and dated decisions.
- `tests/`: test suite mirroring the source tree.

Large datasets, checkpoints, run logs, generated artifacts, and third-party corpus text are local-only by default.

## Current Status

Phase 0 is beginning: repo structure, dependency policy, vocabulary, tokenizer, schemas, contamination checks, and the first reproducibility hooks.

## Development Baseline

The Python environment is managed with `uv` and locked in `uv.lock`.

Set up the dev environment:

```bash
uv sync --extra dev
```

Run the baseline checks:

```bash
uv run --extra dev python scripts/check.py
```

The check runner invokes `ruff check .`, strict `mypy` over current Python files, and `pytest` when test files exist.

> kama pona. ilo ni li lili, taso wile sona ona li suli.
