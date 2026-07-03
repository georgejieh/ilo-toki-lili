from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from data.tokenizer import Tokenizer, detokenize, load_tokenizer


def _minimal_vocab() -> dict[str, Any]:
    return {
        "tokens": [
            {"token_id": 0, "token": "<pad>", "kind": "special"},
            {"token_id": 1, "token": "<bos>", "kind": "special"},
            {"token_id": 2, "token": "<eos>", "kind": "special"},
            {"token_id": 3, "token": "<unk>", "kind": "special"},
            {"token_id": 4, "token": "<name>", "kind": "special"},
            {"token_id": 5, "token": "<img>", "kind": "special"},
            {"token_id": 6, "token": "<sep>", "kind": "special"},
            {"token_id": 7, "token": ".", "kind": "punctuation"},
            {"token_id": 8, "token": "jan", "kind": "word"},
            {"token_id": 9, "token": "<reserved_0>", "kind": "reserved"},
        ],
        "special_tokens": ["<pad>", "<bos>", "<eos>", "<unk>", "<name>", "<img>", "<sep>"],
        "punctuation_tokens": ["."],
        "reserved_tokens": ["<reserved_0>"],
    }


def test_loads_frozen_vocab_registry() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.vocab_size == 152
    assert tokenizer.pad_id == 0
    assert tokenizer.bos_id == 1
    assert tokenizer.eos_id == 2
    assert tokenizer.unk_id == 3
    assert tokenizer.name_id == 4
    assert tokenizer.token_to_id["jan"] == 31
    assert tokenizer.id_to_token[31] == "jan"


def test_tokenize_splits_punctuation_and_specials() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.tokenize('jan Sonja li toki: "soweli li lon!" <sep>') == [
        "jan",
        "Sonja",
        "li",
        "toki",
        ":",
        '"',
        "soweli",
        "li",
        "lon",
        "!",
        '"',
        "<sep>",
    ]


def test_encode_maps_words_punctuation_specials_and_names() -> None:
    tokenizer = load_tokenizer()

    encoded = tokenizer.encode("jan Sonja li lon.", add_bos=True, add_eos=True)

    assert encoded == [
        tokenizer.bos_id,
        tokenizer.token_to_id["jan"],
        tokenizer.name_id,
        tokenizer.token_to_id["li"],
        tokenizer.token_to_id["lon"],
        tokenizer.token_to_id["."],
        tokenizer.eos_id,
    ]


def test_encode_unknown_policy_rejects_high_unknown_fraction() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.encode("jan foo li lon") is None
    assert tokenizer.should_drop("jan foo li lon")


def test_encode_unknown_policy_accepts_at_threshold() -> None:
    tokenizer = load_tokenizer()
    text = "jan jan jan jan jan jan jan jan jan foo"

    encoded = tokenizer.encode(text)

    assert tokenizer.unknown_fraction(text) == 0.1
    assert encoded is not None
    assert encoded[-1] == tokenizer.unk_id


def test_decode_restores_readable_text() -> None:
    tokenizer = load_tokenizer()
    encoded = tokenizer.encode("soweli li lon.", add_bos=True, add_eos=True)

    assert encoded is not None
    assert tokenizer.decode(encoded, skip_special_tokens=True) == "soweli li lon."


def test_reserved_tokens_are_unknown_in_model_visible_text() -> None:
    tokenizer = load_tokenizer()
    encoded = tokenizer.encode_tokens(["<reserved_0>"], reject_over_unk_limit=False)

    assert encoded == [tokenizer.unk_id]


def test_explicit_unk_counts_toward_rejection() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.unknown_fraction_for_tokens(["<unk>"]) == 1.0
    assert tokenizer.encode_tokens(["<unk>"]) is None
    assert tokenizer.encode_tokens(["<unk>"], reject_over_unk_limit=False) == [tokenizer.unk_id]


def test_explicit_name_and_structural_special_encode() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.encode_tokens(["<name>", "<sep>"]) == [
        tokenizer.name_id,
        tokenizer.token_to_id["<sep>"],
    ]


def test_punctuation_only_text_has_no_unknown_fraction() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.unknown_fraction(".,?!") == 0.0
    assert tokenizer.encode(".,?!") == [
        tokenizer.token_to_id["."],
        tokenizer.token_to_id[","],
        tokenizer.token_to_id["?"],
        tokenizer.token_to_id["!"],
    ]


def test_decode_can_keep_special_tokens() -> None:
    tokenizer = load_tokenizer()

    assert tokenizer.decode([tokenizer.bos_id, tokenizer.token_to_id["jan"], tokenizer.eos_id]) == (
        "<bos> jan <eos>"
    )


def test_decode_rejects_unknown_token_id() -> None:
    tokenizer = load_tokenizer()

    with pytest.raises(ValueError, match="Unknown token_id"):
        tokenizer.decode([999])


def test_detokenize_handles_quotes() -> None:
    assert detokenize(["jan", "li", "toki", ":", '"', "soweli", "li", "lon", ".", '"']) == (
        'jan li toki: "soweli li lon."'
    )


def test_detokenize_handles_leading_punctuation_and_lone_quote() -> None:
    assert detokenize(["."]) == "."
    assert detokenize(['"']) == '"'


@pytest.mark.parametrize("max_unknown_fraction", [-0.1, 1.1])
def test_from_vocab_rejects_invalid_unknown_threshold(max_unknown_fraction: float) -> None:
    with pytest.raises(ValueError, match="max_unknown_fraction"):
        Tokenizer.from_vocab(_minimal_vocab(), max_unknown_fraction=max_unknown_fraction)


def test_from_file_rejects_non_object_json(tmp_path: Path) -> None:
    path = tmp_path / "vocab.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="Expected JSON object"):
        Tokenizer.from_file(path)


def test_from_vocab_rejects_non_array_tokens() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"] = "jan"

    with pytest.raises(ValueError, match="Expected array field 'tokens'"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_non_string_special_token_list() -> None:
    vocab = _minimal_vocab()
    vocab["special_tokens"] = ["<pad>", 1]

    with pytest.raises(ValueError, match="Expected string array field 'special_tokens'"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_non_object_token_entry() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"] = ["jan"]

    with pytest.raises(ValueError, match="Each token entry"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_missing_token_string() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"][0] = {"token_id": 0, "token": "", "kind": "special"}

    with pytest.raises(ValueError, match="Expected non-empty string field 'token'"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_non_integer_token_id() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"][0] = {"token_id": "0", "token": "<pad>", "kind": "special"}

    with pytest.raises(ValueError, match="Expected integer field 'token_id'"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_duplicate_token() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"][1] = {"token_id": 1, "token": "<pad>", "kind": "special"}

    with pytest.raises(ValueError, match="Duplicate token"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_duplicate_token_id() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"][1] = {"token_id": 0, "token": "<bos>", "kind": "special"}

    with pytest.raises(ValueError, match="Duplicate token_id"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_non_contiguous_token_ids() -> None:
    vocab = _minimal_vocab()
    vocab["tokens"][-1] = {"token_id": 10, "token": "<reserved_0>", "kind": "reserved"}

    with pytest.raises(ValueError, match="contiguous"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_missing_lexical_special() -> None:
    vocab = _minimal_vocab()
    vocab["special_tokens"] = ["<pad>", "<bos>", "<eos>", "<unk>", "<img>", "<sep>"]

    with pytest.raises(ValueError, match="<name> and <unk>"):
        Tokenizer.from_vocab(vocab)


def test_from_vocab_rejects_missing_structural_special() -> None:
    vocab = _minimal_vocab()
    vocab["special_tokens"] = ["<pad>", "<bos>", "<eos>", "<unk>", "<name>", "<img>"]

    with pytest.raises(ValueError, match="structural special"):
        Tokenizer.from_vocab(vocab)
