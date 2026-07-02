# Eval

Evaluation code turns models and frozen item sets into result artifacts.

Planned modules:

- `items/`: generated evaluation JSONL sets, including frozen E1 through E13 items and E15 domain-shift variants.
- `run_eval.py`: runs applicable evaluations for a model.
- `scoring.py`: forced-choice and parser-verified scoring.
- `stats.py`: confidence intervals and paired tests.
- `report.py`: result artifacts to tables and reports.

Free text should be parsed to predicates or scored through forced choice. String match is not enough for Toki Pona.

E14 is analysis-only and derives from existing outputs. E15 is exploratory robustness work: frozen scenes re-rendered under visual domain shift, plus any small license-cleared human-drawn or photographed simple-scene set. E14 and E15 stay outside the pre-registered headline correction family.
