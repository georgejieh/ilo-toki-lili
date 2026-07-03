from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_BYTES = 1_000_000
PRIVATE_KEY_MARKER = "PRIVATE" + " KEY"
SECRET_PATTERNS = {
    "private key block": re.compile(
        r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?" + PRIVATE_KEY_MARKER + r"-----"
    ),
    "google private key field": re.compile(
        r'"private_key"\s*:\s*"-----BEGIN ' + PRIVATE_KEY_MARKER + r"-----"
    ),
    "openai api key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    "aws access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "aws secret assignment": re.compile(
        r"(?i)\baws[_-]?secret[_-]?access[_-]?key\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{30,}"
    ),
    "wandb api key": re.compile(r"\b[a-f0-9]{40}\b"),
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    label: str


def is_probably_binary(content: bytes) -> bool:
    return b"\0" in content[:4096]


def scan_path(path: Path) -> list[Finding]:
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        return []

    content = path.read_bytes()
    if is_probably_binary(content):
        return []

    text = content.decode("utf-8", errors="ignore")
    findings: list[Finding] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(line) and not is_allowed_false_positive(label, line):
                findings.append(Finding(path=path, line_number=line_number, label=label))

    return findings


def is_allowed_false_positive(label: str, line: str) -> bool:
    return label == "wandb api key" and "commit" in line.lower()


def main(argv: list[str] | None = None) -> int:
    paths = [Path(value) for value in (argv if argv is not None else sys.argv[1:])]
    findings = [finding for path in paths for finding in scan_path(path)]

    if findings:
        for finding in findings:
            message = f"{finding.path}:{finding.line_number}: possible {finding.label}"
            print(message, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
