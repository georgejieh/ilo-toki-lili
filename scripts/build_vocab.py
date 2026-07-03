from __future__ import annotations

# ruff: noqa: E402, I001

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.vocab_builder import build_vocab_artifacts, load_json, sha256_file, write_json

DEFAULT_SOURCE = ROOT / "data" / "linku_source_snapshot.json"
DEFAULT_OUTPUT = ROOT / "data" / "vocab.json"
DEFAULT_MANIFEST = ROOT / "data" / "vocab_source_manifest.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build project vocabulary artifacts.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--generator-commit", required=True)
    parser.add_argument("--generated-date", required=True)
    args = parser.parse_args(argv)

    source_path = _resolve_path(args.source)
    output_path = _resolve_path(args.output)
    manifest_path = _resolve_path(args.manifest)

    snapshot = load_json(source_path)
    vocab, manifest = build_vocab_artifacts(
        snapshot,
        source_snapshot_path=source_path.relative_to(ROOT).as_posix(),
        source_snapshot_sha256=sha256_file(source_path),
        generator_commit=args.generator_commit,
        generated_date=args.generated_date,
    )
    write_json(output_path, vocab)
    write_json(manifest_path, manifest)
    print(f"Wrote {output_path}")
    print(f"Wrote {manifest_path}")
    print(f"Words: {vocab['word_count']}")
    print(f"Tokens: {vocab['token_count']}")
    return 0


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


if __name__ == "__main__":
    sys.exit(main())
