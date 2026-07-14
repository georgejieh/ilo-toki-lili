from __future__ import annotations

import pytest
import yaml

from configs.config_hash import canonical_json, hash_config, make_run_id


def test_canonical_json_is_stable_across_key_order() -> None:
    first = {"b": 1, "a": 2}
    second = {"a": 2, "b": 1}
    assert canonical_json(first) == canonical_json(second)


def test_hash_config_is_key_order_independent() -> None:
    assert hash_config({"b": 1, "a": 2}) == hash_config({"a": 2, "b": 1})


def test_nested_structures_are_canonicalized() -> None:
    config = {
        "model": {"name": "toki-taso", "depth": 4},
        "data": ["train", "valid"],
        "seed": 42,
    }
    expected = '{"data":["train","valid"],"model":{"depth":4,"name":"toki-taso"},"seed":42}'
    assert canonical_json(config) == expected


def test_make_run_id_composes_hash_and_seed() -> None:
    run_id = make_run_id("abc123", 7)
    assert run_id == "abc123-7"


def test_make_run_id_rejects_non_string_hash() -> None:
    with pytest.raises(TypeError, match="config_hash must be a string"):
        make_run_id(123, 7)  # type: ignore[arg-type]


def test_make_run_id_rejects_non_integer_seed() -> None:
    with pytest.raises(TypeError, match="seed must be an integer"):
        make_run_id("abc123", "7")  # type: ignore[arg-type]


def test_rejects_non_string_mapping_keys() -> None:
    with pytest.raises(TypeError, match="Config keys must be strings"):
        canonical_json({1: "value"})  # type: ignore[dict-item]


def test_rejects_nested_non_string_keys() -> None:
    with pytest.raises(TypeError, match="Config keys must be strings"):
        canonical_json({"outer": {1: "inner"}})


def test_rejects_sets() -> None:
    with pytest.raises(TypeError):
        canonical_json({"tags": {"a", "b"}})


def test_yaml_equivalent_produces_same_hash() -> None:
    yaml_text = """
model:
  name: toki-taso
  depth: 4
data:
  - train
  - valid
seed: 42
"""
    from_yaml = yaml.safe_load(yaml_text)
    assert isinstance(from_yaml, dict)
    from_dict = {
        "model": {"name": "toki-taso", "depth": 4},
        "data": ["train", "valid"],
        "seed": 42,
    }
    assert hash_config(from_yaml) == hash_config(from_dict)
