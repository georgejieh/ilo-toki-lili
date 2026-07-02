# Tests

Tests mirror the source layout.

Examples:

- `tests/data/test_tokenizer.py` for `data/tokenizer.py`
- `tests/data/test_schemas.py` for `data/schemas.py`
- `tests/models/test_params.py` for `models/params.py`
- `tests/eval/test_scoring.py` for `eval/scoring.py`

Core checks should cover contamination, holdouts, tokenizer round trips, grammar parse/describe properties, parameter parity, checkpoint resume, and report generation from artifacts.

## Empty Module Policy

Top-level source directories are importable Python packages. Their `__init__.py` files may contain only a package docstring and an empty public export tuple until there is a real API to expose.

Do not add empty implementation modules or empty test files as placeholders. Keep planned module names in the relevant README until the module has executable behavior and focused tests.

Tests mirror the source tree once code exists. For example, `data/tokenizer.py` should be covered by `tests/data/test_tokenizer.py`, and `models/params.py` should be covered by `tests/models/test_params.py`.
