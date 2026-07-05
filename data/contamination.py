"""Core linter for model-visible Toki Pona text contamination."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from data.tokenizer import DEFAULT_VOCAB_PATH, Tokenizer, load_tokenizer

type ContaminationReason = Literal["invalid_utf8", "reserved_token", "unknown_token"]

_ALLOWED_TOKEN_KINDS: Final = frozenset({"word", "punctuation", "special"})
_NAME_INITIALS: Final = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


@dataclass(frozen=True)
class ContaminationFinding:
    token: str
    line_number: int
    column: int
    reason: ContaminationReason
    path: Path | None = None

    def format(self) -> str:
        location = "" if self.path is None else f"{self.path}:"
        return f"{location}{self.line_number}:{self.column}: {self.reason}: {self.token!r}"


@dataclass(frozen=True)
class ContaminationLinter:
    tokenizer: Tokenizer
    allowed_tokens: frozenset[str]
    allow_names: bool = True

    @classmethod
    def from_tokenizer(
        cls,
        tokenizer: Tokenizer,
        *,
        allow_names: bool = True,
    ) -> ContaminationLinter:
        allowed_tokens = frozenset(
            token
            for token, kind in tokenizer.token_kinds.items()
            if kind in _ALLOWED_TOKEN_KINDS
        )
        return cls(tokenizer=tokenizer, allowed_tokens=allowed_tokens, allow_names=allow_names)

    @classmethod
    def from_vocab_file(
        cls,
        path: Path = DEFAULT_VOCAB_PATH,
        *,
        allow_names: bool = True,
    ) -> ContaminationLinter:
        return cls.from_tokenizer(load_tokenizer(path), allow_names=allow_names)

    def lint_path(self, path: Path) -> list[ContaminationFinding]:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return [
                ContaminationFinding(
                    token="<invalid utf-8>",
                    line_number=1,
                    column=1,
                    reason="invalid_utf8",
                    path=path,
                )
            ]
        return self.lint_text(text, path=path)

    def lint_text(self, text: str, *, path: Path | None = None) -> list[ContaminationFinding]:
        findings: list[ContaminationFinding] = []

        for line_number, line in enumerate(text.splitlines(), start=1):
            cursor = 0
            for token in self.tokenizer.tokenize(line):
                column, cursor = _token_position(line, token, cursor)
                reason = self.contamination_reason(token)
                if reason is not None:
                    findings.append(
                        ContaminationFinding(
                            token=token,
                            line_number=line_number,
                            column=column,
                            reason=reason,
                            path=path,
                        )
                    )

        return findings

    def contamination_reason(self, token: str) -> ContaminationReason | None:
        if token in self.tokenizer.reserved_tokens:
            return "reserved_token"
        if token in self.allowed_tokens:
            return None
        if self.allow_names and _is_name_token(token):
            return None
        return "unknown_token"


def load_contamination_linter(
    path: Path = DEFAULT_VOCAB_PATH,
    *,
    allow_names: bool = True,
) -> ContaminationLinter:
    return ContaminationLinter.from_vocab_file(path, allow_names=allow_names)


def lint_text(
    text: str,
    *,
    linter: ContaminationLinter | None = None,
    path: Path | None = None,
) -> list[ContaminationFinding]:
    active_linter = load_contamination_linter() if linter is None else linter
    return active_linter.lint_text(text, path=path)


def lint_paths(
    paths: list[Path],
    *,
    linter: ContaminationLinter | None = None,
) -> list[ContaminationFinding]:
    active_linter = load_contamination_linter() if linter is None else linter
    return [finding for path in paths for finding in active_linter.lint_path(path)]


def _is_name_token(token: str) -> bool:
    return bool(token) and token[0] in _NAME_INITIALS


def _token_position(line: str, token: str, start: int) -> tuple[int, int]:
    index = line.find(token, start)
    if index == -1:
        return start + 1, start
    return index + 1, index + len(token)


__all__ = (
    "ContaminationFinding",
    "ContaminationLinter",
    "ContaminationReason",
    "lint_paths",
    "lint_text",
    "load_contamination_linter",
)
