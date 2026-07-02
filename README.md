# ilo toki lili

ilo toki lili is a small Toki Pona language-modeling project for testing whether grounded training changes model behavior in fundamental ways.

The core comparison is:

1. A standard transformer trained on a text-only corpus.
2. A standard transformer trained on a multimodal grounding corpus.
3. A new grounded architecture trained on the same multimodal grounding corpus.

Toki Pona keeps the language small enough for one-person experiments while still leaving room for meaning, reference, ambiguity, and compositional behavior.

## Repository Layout

- `ilo_toki_lili/`: Python package for reusable code.
- `scripts/`: Small command-line entry points for data preparation, training, and evaluation.
- `experiments/`: Reproducible experiment definitions and public notes.
- `data/`: Placeholder documentation for local datasets. Raw and generated data are ignored by git.
- `tests/`: Test suite.

## Local Data

Large corpora, generated datasets, checkpoints, and run outputs are intentionally excluded from version control. Keep those under `data/`, `checkpoints/`, `outputs/`, or `runs/` as appropriate.

## Status

This project is in early research setup.
