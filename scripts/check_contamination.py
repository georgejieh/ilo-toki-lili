from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.contamination import (  # noqa: E402
    ContaminationFinding,
    ContaminationLinter,
    load_contamination_linter,
)

EXCLUDED_DIRS = {
    ".agents",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}
MODEL_VISIBLE_JSON_KEYS = frozenset(
    {
        "answer",
        "answers",
        "caption",
        "captions",
        "choice",
        "choices",
        "completion",
        "content",
        "option",
        "options",
        "prompt",
        "question",
        "questions",
        "sentence",
        "sentences",
        "target",
        "targets",
        "text",
        "texts",
        "utterance",
        "utterances",
    }
)


def discover_contamination_targets(root: Path = ROOT) -> list[Path]:
    targets: list[Path] = []

    if root.is_file():
        return [root] if _is_supported_target(root) else []

    for directory, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        base = Path(directory)

        for filename in filenames:
            path = base / filename
            if _is_default_target(path, root):
                targets.append(path)

    return sorted(targets)


def lint_targets(
    targets: Sequence[Path],
    *,
    linter: ContaminationLinter | None = None,
) -> list[ContaminationFinding]:
    active_linter = load_contamination_linter() if linter is None else linter
    findings: list[ContaminationFinding] = []

    for target in targets:
        findings.extend(_lint_target(target, active_linter))

    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan model-visible text for contamination.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional files or directories to scan. Defaults to repo model-visible targets.",
    )
    args = parser.parse_args(argv)

    targets = _targets_from_args(args.paths)
    findings = lint_targets(targets)

    if findings:
        for finding in findings:
            print(finding.format(), file=sys.stderr)
        return 1

    return 0


def _targets_from_args(paths: Sequence[Path]) -> list[Path]:
    if not paths:
        return discover_contamination_targets(ROOT)

    targets: list[Path] = []
    for path in paths:
        targets.extend(discover_contamination_targets(path))
    return sorted(targets)


def _lint_target(
    path: Path,
    linter: ContaminationLinter,
) -> list[ContaminationFinding]:
    if path.suffix == ".txt":
        return linter.lint_path(path)
    if path.suffix == ".jsonl":
        return _lint_jsonl_path(path, linter)
    if path.suffix == ".json":
        return _lint_json_path(path, linter)
    return []


def _lint_json_path(
    path: Path,
    linter: ContaminationLinter,
) -> list[ContaminationFinding]:
    try:
        value: object = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return [_path_error(path, "invalid_utf8")]
    except json.JSONDecodeError as error:
        return [_path_error(path, "invalid_json", line_number=error.lineno, column=error.colno)]

    return _lint_model_visible_json_value(value, linter=linter, path=path)


def _lint_jsonl_path(
    path: Path,
    linter: ContaminationLinter,
) -> list[ContaminationFinding]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return [_path_error(path, "invalid_utf8")]

    findings: list[ContaminationFinding] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value: object = json.loads(line)
        except json.JSONDecodeError as error:
            findings.append(
                _path_error(path, "invalid_json", line_number=line_number, column=error.colno)
            )
            continue
        findings.extend(
            _lint_model_visible_json_value(
                value,
                linter=linter,
                path=path,
                line_number=line_number,
            )
        )

    return findings


def _lint_model_visible_json_value(
    value: object,
    *,
    linter: ContaminationLinter,
    path: Path,
    line_number: int | None = None,
) -> list[ContaminationFinding]:
    findings: list[ContaminationFinding] = []
    for text in _iter_model_visible_json_strings(value):
        for finding in linter.lint_text(text, path=path):
            findings.append(
                ContaminationFinding(
                    token=finding.token,
                    line_number=line_number if line_number is not None else finding.line_number,
                    column=finding.column,
                    reason=finding.reason,
                    path=finding.path,
                )
            )
    return findings


def _iter_model_visible_json_strings(value: object, *, visible: bool = False) -> Iterator[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_is_visible = isinstance(key, str) and key in MODEL_VISIBLE_JSON_KEYS
            yield from _iter_model_visible_json_strings(item, visible=visible or key_is_visible)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_model_visible_json_strings(item, visible=visible)
    elif isinstance(value, str) and visible:
        yield value


def _path_error(
    path: Path,
    reason: str,
    *,
    line_number: int = 1,
    column: int = 1,
) -> ContaminationFinding:
    if reason == "invalid_json":
        return ContaminationFinding(
            token="<invalid json>",
            line_number=line_number,
            column=column,
            reason="invalid_json",
            path=path,
        )
    return ContaminationFinding(
        token="<invalid utf-8>",
        line_number=line_number,
        column=column,
        reason="invalid_utf8",
        path=path,
    )


def _is_default_target(path: Path, root: Path) -> bool:
    if path.suffix == ".txt":
        return True
    if path.suffix == ".jsonl":
        return _is_model_artifact_path(path, root)
    if path.suffix == ".json":
        return _is_manifest_path(path, root)
    return False


def _is_supported_target(path: Path) -> bool:
    return path.suffix in {".json", ".jsonl", ".txt"}


def _is_model_artifact_path(path: Path, root: Path) -> bool:
    parts = _relative_parts(path, root)
    return bool(parts) and parts[0] in {"data", "eval"}


def _is_manifest_path(path: Path, root: Path) -> bool:
    name = path.name.lower()
    if name not in {"manifest.json", "shard_manifest.json"} and not name.endswith(".manifest.json"):
        return False

    parts = _relative_parts(path, root)
    return any(part in {"items", "shards", "tiers"} for part in parts)


def _relative_parts(path: Path, root: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(root).parts
    except ValueError:
        return path.parts


if __name__ == "__main__":
    sys.exit(main())
