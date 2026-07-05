from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_contamination import (
    discover_contamination_targets,
    lint_targets,
    main,
)


def test_discovers_text_artifacts_and_model_manifests(tmp_path: Path) -> None:
    text_artifact = tmp_path / "data" / "sample.txt"
    manifest = tmp_path / "data" / "shards" / "sample.manifest.json"
    jsonl = tmp_path / "eval" / "items" / "e1" / "items.jsonl"
    ignored_markdown = tmp_path / "docs" / "note.md"
    ignored_json = tmp_path / "data" / "vocab_source_manifest.json"
    ignored_venv_text = tmp_path / ".venv" / "bad.txt"

    _write_text(text_artifact, "jan li lon.")
    _write_json(manifest, {"samples": [{"text": "soweli li lon.", "metadata": "English ok"}]})
    _write_text(jsonl, json.dumps({"prompt": "seme?", "metadata": "English ok"}) + "\n")
    _write_text(ignored_markdown, "English docs are not model-visible.")
    _write_json(ignored_json, {"artifact": "data/vocab.json"})
    _write_text(ignored_venv_text, "outside")

    assert discover_contamination_targets(tmp_path) == [
        text_artifact,
        manifest,
        jsonl,
    ]


def test_lints_plain_text_targets(tmp_path: Path) -> None:
    clean = tmp_path / "clean.txt"
    dirty = tmp_path / "dirty.txt"
    _write_text(clean, "jan li lon.")
    _write_text(dirty, "jan outside li lon.")

    findings = lint_targets([clean, dirty])

    assert [(finding.path, finding.token, finding.reason) for finding in findings] == [
        (dirty, "outside", "unknown_token")
    ]


def test_lints_only_model_visible_json_fields(tmp_path: Path) -> None:
    manifest = tmp_path / "sample.manifest.json"
    _write_json(
        manifest,
        {
            "text": "jan outside li lon.",
            "metadata": "English metadata is allowed here",
        },
    )

    findings = lint_targets([manifest])

    assert [(finding.token, finding.reason) for finding in findings] == [
        ("outside", "unknown_token")
    ]


def test_lints_jsonl_records_with_record_line_number(tmp_path: Path) -> None:
    jsonl = tmp_path / "items.jsonl"
    _write_text(
        jsonl,
        "\n".join(
            [
                json.dumps({"prompt": "jan li lon."}),
                json.dumps({"choices": ["lon", "outside"]}),
            ]
        )
        + "\n",
    )

    findings = lint_targets([jsonl])

    assert [(finding.token, finding.line_number, finding.reason) for finding in findings] == [
        ("outside", 2, "unknown_token")
    ]


def test_reports_invalid_json(tmp_path: Path) -> None:
    manifest = tmp_path / "bad.manifest.json"
    _write_text(manifest, '{"text":')

    findings = lint_targets([manifest])

    assert [(finding.token, finding.line_number, finding.reason) for finding in findings] == [
        ("<invalid json>", 1, "invalid_json")
    ]


def test_main_returns_nonzero_for_contamination(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    dirty = tmp_path / "dirty.txt"
    _write_text(dirty, "outside")

    assert main([str(tmp_path)]) == 1

    captured = capsys.readouterr()
    assert "unknown_token" in captured.err
    assert "outside" in captured.err


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, value: object) -> None:
    _write_text(path, json.dumps(value) + "\n")
