from __future__ import annotations

from pathlib import Path

from data.contamination import (
    ContaminationFinding,
    ContaminationLinter,
    lint_paths,
    lint_text,
    load_contamination_linter,
)


def test_default_linter_accepts_vocab_punctuation_specials_and_names() -> None:
    text = 'jan Sonja li toki: "soweli li lon!" <sep> <unk>'

    assert lint_text(text) == []


def test_linter_reports_unknown_and_reserved_tokens_with_locations() -> None:
    linter = load_contamination_linter()
    text = "jan li lon.\nthis word li lon;\n<reserved_0> jan"

    findings = linter.lint_text(text)

    observed = [
        (finding.token, finding.line_number, finding.column, finding.reason) for finding in findings
    ]

    assert observed == [
        ("this", 2, 1, "unknown_token"),
        ("word", 2, 6, "unknown_token"),
        ("lon;", 2, 14, "unknown_token"),
        ("<reserved_0>", 3, 1, "reserved_token"),
    ]


def test_linter_can_disallow_raw_name_tokens() -> None:
    linter = ContaminationLinter.from_tokenizer(
        load_contamination_linter().tokenizer,
        allow_names=False,
    )

    findings = linter.lint_text("jan Sonja li lon.")

    assert [(finding.token, finding.reason) for finding in findings] == [("Sonja", "unknown_token")]


def test_lint_path_reads_utf8_text_and_preserves_path(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("jan li lon.\nhello", encoding="utf-8")

    findings = load_contamination_linter().lint_path(path)

    assert findings == [
        ContaminationFinding(
            token="hello",
            line_number=2,
            column=1,
            reason="unknown_token",
            path=path,
        )
    ]
    assert findings[0].format() == f"{path}:2:1: unknown_token: 'hello'"


def test_lint_path_reports_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_bytes(b"jan li lon.\xff")

    findings = load_contamination_linter().lint_path(path)

    assert findings == [
        ContaminationFinding(
            token="<invalid utf-8>",
            line_number=1,
            column=1,
            reason="invalid_utf8",
            path=path,
        )
    ]


def test_lint_paths_aggregates_findings(tmp_path: Path) -> None:
    clean = tmp_path / "clean.txt"
    dirty = tmp_path / "dirty.txt"
    clean.write_text("jan li lon.", encoding="utf-8")
    dirty.write_text("jan li outside.", encoding="utf-8")

    findings = lint_paths([clean, dirty])

    assert [(finding.path, finding.token) for finding in findings] == [(dirty, "outside")]
