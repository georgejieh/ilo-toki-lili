# Eval

Evaluation code turns models and frozen item sets into result artifacts.

Planned modules:

- `items/`: generated evaluation JSONL sets.
- `run_eval.py`: runs applicable evaluations for a model.
- `scoring.py`: forced-choice and parser-verified scoring.
- `stats.py`: confidence intervals and paired tests.
- `report.py`: result artifacts to tables and reports.

Free text should be parsed to predicates or scored through forced choice. String match is not enough for Toki Pona.
