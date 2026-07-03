"""Build the project vocabulary from a compact Linku source snapshot."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, cast

Partition = Literal["GROUND_VISUAL", "GROUND_TEMPORAL", "FUNCTION", "DEFERRED"]

TARGET_WORD_COUNT: Final = 137
SELECTED_BOOKS: Final = ("pu", "ku suli")
SPECIAL_TOKENS: Final = ("<pad>", "<bos>", "<eos>", "<unk>", "<name>", "<img>", "<sep>")
PUNCTUATION_TOKENS: Final = (".", ",", "?", "!", ":", '"')
RESERVED_TOKENS: Final = ("<reserved_0>", "<reserved_1>")
VALID_PARTITIONS: Final = ("GROUND_VISUAL", "GROUND_TEMPORAL", "FUNCTION", "DEFERRED")

FUNCTION_WORDS: Final = frozenset(
    {
        "a",
        "ala",
        "anu",
        "e",
        "en",
        "la",
        "li",
        "ni",
        "o",
        "pi",
        "seme",
        "taso",
    }
)

GROUND_VISUAL_WORDS: Final = frozenset(
    {
        "akesi",
        "ale",
        "anpa",
        "esun",
        "ijo",
        "insa",
        "ilo",
        "jaki",
        "jan",
        "jelo",
        "kala",
        "kasi",
        "kijetesantakalu",
        "kili",
        "kiwen",
        "ko",
        "kon",
        "kule",
        "kute",
        "laso",
        "leko",
        "len",
        "lete",
        "lili",
        "linja",
        "lipu",
        "loje",
        "lon",
        "luka",
        "lupa",
        "ma",
        "mani",
        "misikeke",
        "moku",
        "monsi",
        "mun",
        "mute",
        "namako",
        "nanpa",
        "nena",
        "noka",
        "oko",
        "palisa",
        "pan",
        "pimeja",
        "pipi",
        "poka",
        "poki",
        "seli",
        "selo",
        "sewi",
        "sijelo",
        "sike",
        "sinpin",
        "sitelen",
        "soko",
        "soweli",
        "suli",
        "suno",
        "supa",
        "suwi",
        "telo",
        "tomo",
        "tu",
        "uta",
        "walo",
        "wan",
        "waso",
    }
)

GROUND_TEMPORAL_WORDS: Final = frozenset(
    {
        "alasa",
        "awen",
        "jo",
        "kalama",
        "kama",
        "kepeken",
        "kipisi",
        "lanpan",
        "lape",
        "lukin",
        "moli",
        "mu",
        "musi",
        "open",
        "pakala",
        "pali",
        "pana",
        "pini",
        "sin",
        "tan",
        "tawa",
        "tenpo",
        "toki",
        "utala",
        "weka",
    }
)


@dataclass(frozen=True)
class SnapshotWord:
    id: str
    word: str
    book: str
    usage_category: str
    deprecated: bool
    source_path: str
    source_sha256: str
    parent_id: str | None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> SnapshotWord:
        parent = value.get("parent_id")
        if parent is not None and not isinstance(parent, str):
            raise ValueError(f"Invalid parent_id for {value.get('word')!r}")

        return cls(
            id=_required_str(value, "id"),
            word=_required_str(value, "word"),
            book=_required_str(value, "book"),
            usage_category=_required_str(value, "usage_category"),
            deprecated=_required_bool(value, "deprecated"),
            source_path=_required_str(value, "source_path"),
            source_sha256=_required_str(value, "source_sha256"),
            parent_id=parent,
        )

    @property
    def selected(self) -> bool:
        return self.book in SELECTED_BOOKS and not self.deprecated and self.parent_id is None


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return cast(dict[str, Any], value)


def sha256_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def build_vocab_artifacts(
    snapshot: Mapping[str, Any],
    *,
    source_snapshot_path: str,
    source_snapshot_sha256: str,
    generator_commit: str,
    generated_date: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    upstream = _required_mapping(snapshot, "upstream")
    source_files = _required_sequence(snapshot, "source_files")
    snapshot_words = _load_snapshot_words(snapshot)
    selected_words = sorted(
        (word for word in snapshot_words if word.selected),
        key=lambda item: item.word,
    )

    if len(selected_words) != TARGET_WORD_COUNT:
        raise ValueError(
            f"Expected {TARGET_WORD_COUNT} selected words from Linku snapshot; "
            f"found {len(selected_words)}"
        )

    words = [_word_entry(word, index) for index, word in enumerate(selected_words)]
    token_count = len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS) + len(words) + len(RESERVED_TOKENS)

    vocab = {
        "schema_version": 1,
        "status": "draft",
        "language": "tok",
        "word_count": len(words),
        "token_count": token_count,
        "special_tokens": list(SPECIAL_TOKENS),
        "punctuation_tokens": list(PUNCTUATION_TOKENS),
        "reserved_tokens": list(RESERVED_TOKENS),
        "selection": {
            "book_values": list(SELECTED_BOOKS),
            "exclude_deprecated": True,
            "exclude_parent_entries": True,
        },
        "source": {
            "snapshot_path": source_snapshot_path,
            "snapshot_sha256": source_snapshot_sha256,
            "upstream_repository": _required_str(upstream, "repository"),
            "upstream_commit": _required_str(upstream, "commit"),
            "upstream_license": _required_str(upstream, "license"),
            "retrieved_at": _required_str(snapshot, "retrieved_at"),
        },
        "words": words,
    }

    manifest = {
        "schema_version": 1,
        "artifact": "data/vocab.json",
        "artifact_status": "draft",
        "generated_date": generated_date,
        "generator": "scripts/build_vocab.py",
        "generator_commit": generator_commit,
        "source_snapshot": source_snapshot_path,
        "source_snapshot_sha256": source_snapshot_sha256,
        "upstream_repository": _required_str(upstream, "repository"),
        "upstream_commit": _required_str(upstream, "commit"),
        "upstream_license": _required_str(upstream, "license"),
        "retrieved_at": _required_str(snapshot, "retrieved_at"),
        "selection": vocab["selection"],
        "source_file_count": len(source_files),
        "selected_word_count": len(words),
        "token_count": token_count,
    }
    return vocab, manifest


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def partition_for_word(word: str) -> Partition:
    if word in FUNCTION_WORDS:
        return "FUNCTION"
    if word in GROUND_TEMPORAL_WORDS:
        return "GROUND_TEMPORAL"
    if word in GROUND_VISUAL_WORDS:
        return "GROUND_VISUAL"
    return "DEFERRED"


def _word_entry(word: SnapshotWord, word_index: int) -> dict[str, Any]:
    token_id = len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS) + word_index
    return {
        "token_id": token_id,
        "word": word.word,
        "linku_id": word.id,
        "book": word.book,
        "partition": partition_for_word(word.word),
        "linku_usage_category": word.usage_category,
        "source_path": word.source_path,
        "source_sha256": word.source_sha256,
    }


def _load_snapshot_words(snapshot: Mapping[str, Any]) -> list[SnapshotWord]:
    words = _required_sequence(snapshot, "words")
    parsed: list[SnapshotWord] = []
    seen: set[str] = set()

    for value in words:
        if not isinstance(value, Mapping):
            raise ValueError("Each snapshot word must be an object")
        word = SnapshotWord.from_mapping(value)
        if word.word in seen:
            raise ValueError(f"Duplicate snapshot word {word.word!r}")
        seen.add(word.word)
        parsed.append(word)

    return parsed


def _required_bool(value: Mapping[str, Any], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ValueError(f"Expected boolean field {key!r}")
    return item


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ValueError(f"Expected object field {key!r}")
    return item


def _required_sequence(value: Mapping[str, Any], key: str) -> Sequence[Any]:
    item = value.get(key)
    if not isinstance(item, Sequence) or isinstance(item, str):
        raise ValueError(f"Expected array field {key!r}")
    return item


def _required_str(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError(f"Expected non-empty string field {key!r}")
    return item
