from __future__ import annotations

from pathlib import Path
from typing import Any

from data.vocab_builder import (
    PUNCTUATION_TOKENS,
    RESERVED_TOKENS,
    SPECIAL_TOKENS,
    TARGET_WORD_COUNT,
    VALID_PARTITIONS,
    VOCAB_SCHEMA_VERSION,
    VOCAB_STATUS,
    build_vocab_artifacts,
    load_json,
    partition_for_word,
    sha256_file,
)

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "data" / "linku_source_snapshot.json"
VOCAB_PATH = ROOT / "data" / "vocab.json"
MANIFEST_PATH = ROOT / "data" / "vocab_source_manifest.json"


def test_partition_examples_follow_master_plan() -> None:
    assert partition_for_word("li") == "FUNCTION"
    assert partition_for_word("nanpa") == "FUNCTION"
    assert partition_for_word("jan") == "GROUND_VISUAL"
    assert partition_for_word("ale") == "GROUND_VISUAL"
    assert partition_for_word("kute") == "GROUND_VISUAL"
    assert partition_for_word("tawa") == "GROUND_TEMPORAL"
    assert partition_for_word("tenpo") == "GROUND_TEMPORAL"
    assert partition_for_word("kalama") == "DEFERRED"
    assert partition_for_word("kon") == "DEFERRED"
    assert partition_for_word("mu") == "DEFERRED"
    assert partition_for_word("mi") == "DEFERRED"
    assert partition_for_word("sina") == "DEFERRED"
    assert partition_for_word("ona") == "DEFERRED"
    assert partition_for_word("pona") == "DEFERRED"
    assert partition_for_word("toki") == "DEFERRED"


def test_generated_vocab_matches_snapshot() -> None:
    snapshot = load_json(SNAPSHOT_PATH)
    vocab = load_json(VOCAB_PATH)
    manifest = load_json(MANIFEST_PATH)

    rebuilt_vocab, rebuilt_manifest = build_vocab_artifacts(
        snapshot,
        source_snapshot_path="data/linku_source_snapshot.json",
        source_snapshot_sha256=sha256_file(SNAPSHOT_PATH),
        generator_commit=_required_str(manifest, "generator_commit"),
        generated_date=_required_str(manifest, "generated_date"),
    )

    assert vocab == rebuilt_vocab
    assert manifest == rebuilt_manifest


def test_vocab_contract() -> None:
    vocab = load_json(VOCAB_PATH)
    words = _required_list(vocab, "words")

    assert vocab["schema_version"] == VOCAB_SCHEMA_VERSION
    assert vocab["status"] == VOCAB_STATUS
    assert vocab["word_count"] == TARGET_WORD_COUNT
    assert len(words) == TARGET_WORD_COUNT
    assert vocab["special_tokens"] == list(SPECIAL_TOKENS)
    assert vocab["punctuation_tokens"] == list(PUNCTUATION_TOKENS)
    assert vocab["reserved_tokens"] == list(RESERVED_TOKENS)
    assert vocab["token_count"] == (
        len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS) + len(words) + len(RESERVED_TOKENS)
    )

    word_strings = [_required_str(word, "word") for word in words]
    assert word_strings == sorted(word_strings)
    assert len(set(word_strings)) == TARGET_WORD_COUNT
    assert "ali" not in word_strings
    assert {"ale", "kijetesantakalu", "namako", "oko"}.issubset(word_strings)

    token_ids = [_required_int(word, "token_id") for word in words]
    first_word_token_id = len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS)
    assert token_ids == list(range(first_word_token_id, first_word_token_id + TARGET_WORD_COUNT))

    partitions = {_required_str(word, "partition") for word in words}
    assert partitions <= set(VALID_PARTITIONS)
    assert partitions == set(VALID_PARTITIONS)


def test_token_registry_contract() -> None:
    vocab = load_json(VOCAB_PATH)
    words = _required_list(vocab, "words")
    tokens = _required_list(vocab, "tokens")

    token_ids = [_required_int(token, "token_id") for token in tokens]
    token_strings = [_required_str(token, "token") for token in tokens]

    assert token_ids == list(range(_required_int(vocab, "token_count")))
    assert len(set(token_strings)) == len(tokens)
    assert token_strings[: len(SPECIAL_TOKENS)] == list(SPECIAL_TOKENS)
    punctuation_end = len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS)
    assert token_strings[len(SPECIAL_TOKENS) : punctuation_end] == list(PUNCTUATION_TOKENS)
    assert token_strings[-len(RESERVED_TOKENS) :] == list(RESERVED_TOKENS)

    word_token_start = len(SPECIAL_TOKENS) + len(PUNCTUATION_TOKENS)
    word_tokens = tokens[word_token_start : word_token_start + TARGET_WORD_COUNT]
    assert [_required_str(token, "kind") for token in word_tokens] == ["word"] * TARGET_WORD_COUNT
    assert [_required_str(token, "token") for token in word_tokens] == [
        _required_str(word, "word") for word in words
    ]


def test_source_manifest_contract() -> None:
    snapshot = load_json(SNAPSHOT_PATH)
    manifest = load_json(MANIFEST_PATH)

    assert manifest["artifact"] == "data/vocab.json"
    assert manifest["artifact_schema_version"] == VOCAB_SCHEMA_VERSION
    assert manifest["artifact_status"] == VOCAB_STATUS
    assert manifest["freeze_decision"] == "docs/decisions/2026-07-03-vocabulary-freeze.md"
    assert manifest["source_snapshot"] == "data/linku_source_snapshot.json"
    assert manifest["source_snapshot_sha256"] == sha256_file(SNAPSHOT_PATH)
    assert manifest["upstream_repository"] == snapshot["upstream"]["repository"]
    assert manifest["upstream_commit"] == snapshot["upstream"]["commit"]
    assert manifest["upstream_license"] == "CC-BY-SA-4.0"
    assert manifest["source_file_count"] == len(_required_list(snapshot, "source_files"))
    assert manifest["selected_word_count"] == TARGET_WORD_COUNT


def _required_int(value: Any, key: str) -> int:
    if not isinstance(value, dict):
        raise TypeError("Expected dict")
    item = value.get(key)
    if not isinstance(item, int):
        raise TypeError(f"Expected int field {key}")
    return item


def _required_list(value: dict[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise TypeError(f"Expected list field {key}")
    return item


def _required_str(value: Any, key: str) -> str:
    if not isinstance(value, dict):
        raise TypeError("Expected dict")
    item = value.get(key)
    if not isinstance(item, str):
        raise TypeError(f"Expected str field {key}")
    return item
