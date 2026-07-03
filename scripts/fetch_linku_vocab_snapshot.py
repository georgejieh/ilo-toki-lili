from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMIT = "d73c4921c63d239d9f96972356c2fcf86a767b1c"
DEFAULT_OUTPUT = ROOT / "data" / "linku_source_snapshot.json"
REPOSITORY = "https://github.com/lipu-linku/sona"
API_BASE = "https://api.github.com/repos/lipu-linku/sona"
LICENSE = "CC-BY-SA-4.0"
USER_AGENT = "ilo-toki-lili-vocab-builder/0.1"


def fetch_json(url: str) -> Any:
    payload = fetch_bytes(url)
    return json.loads(payload.decode("utf-8"))


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    if not isinstance(payload, bytes):
        raise TypeError(f"Expected bytes response from {url}")
    return payload


def build_snapshot(commit: str, retrieved_at: str) -> dict[str, Any]:
    listing = fetch_json(f"{API_BASE}/contents/words/metadata?ref={commit}")
    if not isinstance(listing, list):
        raise ValueError("GitHub contents API returned a non-list response")

    source_files: list[dict[str, Any]] = []
    words: list[dict[str, Any]] = []

    for item in sorted(_content_items(listing), key=lambda entry: entry["path"]):
        text = fetch_bytes(item["download_url"]).decode("utf-8")
        source_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        parsed = tomllib.loads(text)

        source_files.append(
            {
                "path": item["path"],
                "sha256": source_sha256,
                "bytes": len(text.encode("utf-8")),
            }
        )
        words.append(_word_snapshot(parsed, item["path"], source_sha256))

    return {
        "schema_version": 1,
        "retrieved_at": retrieved_at,
        "upstream": {
            "repository": REPOSITORY,
            "commit": commit,
            "license": LICENSE,
            "source_directory": "words/metadata",
        },
        "source_files": source_files,
        "words": sorted(words, key=lambda word: word["word"]),
    }


def write_snapshot(path: Path, snapshot: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a compact Linku vocabulary snapshot.")
    parser.add_argument("--commit", default=DEFAULT_COMMIT, help="Pinned lipu-linku/sona commit.")
    parser.add_argument(
        "--retrieved-at",
        required=True,
        help="UTC date or timestamp recorded in the output manifest.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON snapshot path.",
    )
    args = parser.parse_args(argv)

    snapshot = build_snapshot(commit=args.commit, retrieved_at=args.retrieved_at)
    write_snapshot(args.output, snapshot)
    print(f"Wrote {args.output}")
    print(f"Words: {len(snapshot['words'])}")
    print(f"Source files: {len(snapshot['source_files'])}")
    return 0


def _content_items(value: Sequence[Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("GitHub contents item is not an object")
        name = _required_str(item, "name")
        path = _required_str(item, "path")
        download_url = _required_str(item, "download_url")
        if name.endswith(".toml"):
            items.append({"name": name, "path": path, "download_url": download_url})
    return items


def _word_snapshot(
    parsed: Mapping[str, Any],
    source_path: str,
    source_sha256: str,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": _required_str(parsed, "id"),
        "word": _required_str(parsed, "word"),
        "book": _required_str(parsed, "book"),
        "usage_category": _required_str(parsed, "usage_category"),
        "deprecated": _required_bool(parsed, "deprecated"),
        "source_path": source_path,
        "source_sha256": source_sha256,
    }

    parent_id = parsed.get("parent_id")
    if parent_id is not None:
        if not isinstance(parent_id, str):
            raise ValueError(f"Invalid parent_id in {source_path}")
        value["parent_id"] = parent_id

    return value


def _required_bool(value: Mapping[str, Any], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ValueError(f"Expected boolean field {key!r}")
    return item


def _required_str(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError(f"Expected non-empty string field {key!r}")
    return item


if __name__ == "__main__":
    sys.exit(main())
