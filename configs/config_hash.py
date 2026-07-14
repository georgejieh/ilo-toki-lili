"""Deterministic config canonicalization and run ID generation."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any

__all__ = ("canonical_json", "hash_config", "make_run_id")


def canonical_json(config: Mapping[str, Any]) -> str:
    """Return a stable, compact JSON canonicalization of a config mapping."""
    canonical = _canonicalize(config)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_config(config: Mapping[str, Any]) -> str:
    """Return a SHA-256 hex digest of the canonical JSON of a config mapping."""
    return hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest()


def make_run_id(config_hash: str, seed: int) -> str:
    """Return a run id composed from a config hash and seed."""
    if not isinstance(config_hash, str):
        raise TypeError(f"config_hash must be a string, got {type(config_hash).__name__}")
    if not isinstance(seed, int):
        raise TypeError(f"seed must be an integer, got {type(seed).__name__}")
    return f"{config_hash}-{seed}"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, (str, int, type(None))):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError(f"Non-finite float cannot be canonicalized: {value!r}")
        return value
    if isinstance(value, Mapping):
        for key in value:
            if not isinstance(key, str):
                raise TypeError(f"Config keys must be strings, got {type(key).__name__}")
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        raise TypeError("Sets cannot be canonicalized")
    raise TypeError(f"Value cannot be canonicalized: {type(value).__name__}")
