from __future__ import annotations

import pytest

from data.tokenizer import detokenize, load_tokenizer


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


def test_decode_rejects_unknown_token_id() -> None:
    tokenizer = load_tokenizer()

    with pytest.raises(ValueError, match="Unknown token_id"):
        tokenizer.decode([999])


def test_detokenize_handles_quotes() -> None:
    assert detokenize(["jan", "li", "toki", ":", '"', "soweli", "li", "lon", ".", '"']) == (
        'jan li toki: "soweli li lon."'
    )
