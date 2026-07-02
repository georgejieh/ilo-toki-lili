# Grammar

This directory will contain the Toki Pona grammar and the conversion layer between scene semantics and language.

Planned files:

- `tp.lark`: grammar.
- `describe.py`: scene or episode to Toki Pona descriptions.
- `parse.py`: Toki Pona text to predicates.
- `style.py`: calque filters and corpus style checks.

The same grammar must drive generation and evaluation parsing so training data and scoring do not drift apart.
