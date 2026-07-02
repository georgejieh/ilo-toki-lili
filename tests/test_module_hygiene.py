from __future__ import annotations

import importlib
from types import ModuleType

TOP_LEVEL_MODULES = ("data", "models", "train", "eval")


def test_top_level_modules_import() -> None:
    for module_name in TOP_LEVEL_MODULES:
        module = importlib.import_module(module_name)
        assert isinstance(module, ModuleType)


def test_top_level_modules_export_no_placeholder_api() -> None:
    for module_name in TOP_LEVEL_MODULES:
        module = importlib.import_module(module_name)
        assert module.__all__ == ()
