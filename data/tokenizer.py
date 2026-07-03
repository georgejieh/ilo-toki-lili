"""Closed-vocabulary word tokenizer for the frozen Toki Pona token registry."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast

DEFAULT_VOCAB_PATH: Final = Path(__file__).with_name("vocab.json")
DEFAULT_MAX_UNKNOWN_FRACTION: Final = 0.10

_TOKEN_PATTERN: Final = re.compile(r'<[A-Za-z0-9_]+>|[.,?!:"]|[^\s.,?!:"]+')
_NAME_INITIALS: Final = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_LEFT_ATTACHING_PUNCTUATION: Final = frozenset({".", ",", "?", "!", ":"})
_LEXICAL_SPECIALS: Final = frozenset({"<name>", "<unk>"})
_STRUCTURAL_SPECIALS: Final = frozenset({"<pad>", "<bos>", "<eos>", "<img>", "<sep>"})


@dataclass(frozen=True)
class Tokenizer:
    """Tokenizer backed by the project vocabulary artifact."""

    token_to_id: dict[str, int]
    id_to_token: dict[int, str]
    token_kinds: dict[str, str]
    special_tokens: frozenset[str]
    punctuation_tokens: frozenset[str]
    reserved_tokens: frozenset[str]
    max_unknown_fraction: float = DEFAULT_MAX_UNKNOWN_FRACTION

    @classmethod
    def from_file(
        cls,
        path: Path = DEFAULT_VOCAB_PATH,
        *,
        max_unknown_fraction: float = DEFAULT_MAX_UNKNOWN_FRACTION,
    ) -> Tokenizer:
        return cls.from_vocab(_load_json(path), max_unknown_fraction=max_unknown_fraction)

    @classmethod
    def from_vocab(
        cls,
        value: Mapping[str, Any],
        *,
        max_unknown_fraction: float = DEFAULT_MAX_UNKNOWN_FRACTION,
    ) -> Tokenizer:
        if not 0 <= max_unknown_fraction <= 1:
            raise ValueError("max_unknown_fraction must be between 0 and 1")

        tokens = _required_list(value, "tokens")
        special_tokens = frozenset(_required_str_list(value, "special_tokens"))
        punctuation_tokens = frozenset(_required_str_list(value, "punctuation_tokens"))
        reserved_tokens = frozenset(_required_str_list(value, "reserved_tokens"))

        token_to_id: dict[str, int] = {}
        id_to_token: dict[int, str] = {}
        token_kinds: dict[str, str] = {}

        for entry in tokens:
            if not isinstance(entry, Mapping):
                raise ValueError("Each token entry must be an object")
            token = _required_str(entry, "token")
            token_id = _required_int(entry, "token_id")
            kind = _required_str(entry, "kind")
            if token in token_to_id:
                raise ValueError(f"Duplicate token {token!r}")
            if token_id in id_to_token:
                raise ValueError(f"Duplicate token_id {token_id}")
            token_to_id[token] = token_id
            id_to_token[token_id] = token
            token_kinds[token] = kind

        expected_ids = list(range(len(tokens)))
        if sorted(id_to_token) != expected_ids:
            raise ValueError("Token IDs must be contiguous from zero")

        if not _LEXICAL_SPECIALS <= special_tokens:
            raise ValueError("Vocabulary must define <name> and <unk> special tokens")
        if not _STRUCTURAL_SPECIALS <= special_tokens:
            raise ValueError("Vocabulary is missing required structural special tokens")

        return cls(
            token_to_id=token_to_id,
            id_to_token=id_to_token,
            token_kinds=token_kinds,
            special_tokens=special_tokens,
            punctuation_tokens=punctuation_tokens,
            reserved_tokens=reserved_tokens,
            max_unknown_fraction=max_unknown_fraction,
        )

    @property
    def vocab_size(self) -> int:
        return len(self.token_to_id)

    @property
    def pad_id(self) -> int:
        return self.token_to_id["<pad>"]

    @property
    def bos_id(self) -> int:
        return self.token_to_id["<bos>"]

    @property
    def eos_id(self) -> int:
        return self.token_to_id["<eos>"]

    @property
    def unk_id(self) -> int:
        return self.token_to_id["<unk>"]

    @property
    def name_id(self) -> int:
        return self.token_to_id["<name>"]

    def tokenize(self, text: str) -> list[str]:
        return _TOKEN_PATTERN.findall(text)

    def encode(
        self,
        text: str,
        *,
        add_bos: bool = False,
        add_eos: bool = False,
        reject_over_unk_limit: bool = True,
    ) -> list[int] | None:
        return self.encode_tokens(
            self.tokenize(text),
            add_bos=add_bos,
            add_eos=add_eos,
            reject_over_unk_limit=reject_over_unk_limit,
        )

    def encode_tokens(
        self,
        tokens: Sequence[str],
        *,
        add_bos: bool = False,
        add_eos: bool = False,
        reject_over_unk_limit: bool = True,
    ) -> list[int] | None:
        normalized, unknown_count, lexical_count = self._normalize_tokens(tokens)
        if reject_over_unk_limit and _exceeds_unknown_limit(
            unknown_count,
            lexical_count,
            self.max_unknown_fraction,
        ):
            return None

        if add_bos:
            normalized.insert(0, "<bos>")
        if add_eos:
            normalized.append("<eos>")

        return [self.token_to_id[token] for token in normalized]

    def unknown_fraction(self, text: str) -> float:
        return self.unknown_fraction_for_tokens(self.tokenize(text))

    def unknown_fraction_for_tokens(self, tokens: Sequence[str]) -> float:
        _, unknown_count, lexical_count = self._normalize_tokens(tokens)
        if lexical_count == 0:
            return 0.0
        return unknown_count / lexical_count

    def should_drop(self, text: str) -> bool:
        return self.unknown_fraction(text) > self.max_unknown_fraction

    def decode_tokens(
        self,
        token_ids: Sequence[int],
        *,
        skip_special_tokens: bool = False,
    ) -> list[str]:
        tokens: list[str] = []
        for token_id in token_ids:
            token = self.id_to_token.get(token_id)
            if token is None:
                raise ValueError(f"Unknown token_id {token_id}")
            if skip_special_tokens and token in self.special_tokens:
                continue
            tokens.append(token)
        return tokens

    def decode(
        self,
        token_ids: Sequence[int],
        *,
        skip_special_tokens: bool = False,
    ) -> str:
        return detokenize(self.decode_tokens(token_ids, skip_special_tokens=skip_special_tokens))

    def _normalize_tokens(self, tokens: Sequence[str]) -> tuple[list[str], int, int]:
        normalized: list[str] = []
        unknown_count = 0
        lexical_count = 0

        for token in tokens:
            if token == "<unk>":
                normalized.append(token)
                unknown_count += 1
                lexical_count += 1
                continue
            if token == "<name>" or _is_name_token(token):
                normalized.append("<name>")
                lexical_count += 1
                continue

            kind = self.token_kinds.get(token)
            if kind == "word":
                normalized.append(token)
                lexical_count += 1
            elif kind == "punctuation" or token in _STRUCTURAL_SPECIALS:
                normalized.append(token)
            else:
                normalized.append("<unk>")
                unknown_count += 1
                lexical_count += 1

        return normalized, unknown_count, lexical_count


def load_tokenizer(
    path: Path = DEFAULT_VOCAB_PATH,
    *,
    max_unknown_fraction: float = DEFAULT_MAX_UNKNOWN_FRACTION,
) -> Tokenizer:
    return Tokenizer.from_file(path, max_unknown_fraction=max_unknown_fraction)


def detokenize(tokens: Sequence[str]) -> str:
    parts: list[str] = []
    quote_is_open = False

    for token in tokens:
        if token in _LEFT_ATTACHING_PUNCTUATION and parts:
            parts[-1] = f"{parts[-1]}{token}"
        elif token == '"' and parts and quote_is_open:
            parts[-1] = f'{parts[-1]}"'
            quote_is_open = False
        else:
            parts.append(token)
            if token == '"':
                quote_is_open = True

    return " ".join(parts).replace('" ', '"')


def _is_name_token(token: str) -> bool:
    return bool(token) and token[0] in _NAME_INITIALS


def _exceeds_unknown_limit(
    unknown_count: int,
    lexical_count: int,
    max_unknown_fraction: float,
) -> bool:
    return lexical_count > 0 and (unknown_count / lexical_count) > max_unknown_fraction


def _load_json(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected JSON object in {path}")
    return cast(Mapping[str, Any], value)


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ValueError(f"Expected array field {key!r}")
    return item


def _required_str_list(value: Mapping[str, Any], key: str) -> list[str]:
    items = _required_list(value, key)
    if not all(isinstance(item, str) for item in items):
        raise ValueError(f"Expected string array field {key!r}")
    return cast(list[str], items)


def _required_str(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError(f"Expected non-empty string field {key!r}")
    return item


def _required_int(value: Mapping[str, Any], key: str) -> int:
    item = value.get(key)
    if not isinstance(item, int):
        raise ValueError(f"Expected integer field {key!r}")
    return item
