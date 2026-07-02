# Tests

Tests mirror the source layout.

Examples:

- `tests/data/test_tokenizer.py` for `data/tokenizer.py`
- `tests/data/test_schemas.py` for `data/schemas.py`
- `tests/models/test_params.py` for `models/params.py`
- `tests/eval/test_scoring.py` for `eval/scoring.py`

Core checks should cover contamination, holdouts, tokenizer round trips, grammar parse/describe properties, parameter parity, checkpoint resume, and report generation from artifacts.
