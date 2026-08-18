#!/usr/bin/env python3
"""Lightweight content quality checker for the guest guide.

Run before every build (locally or in CI). Fails the build only on
issues that would break the published site — a missing page heading or
a relative link that points nowhere. Placeholder content is expected
at this stage of the project and is only reported as a warning.

Usage: python scripts/check_content.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
PLACEHOLDER_MARKERS = ("TODO", "PLACEHOLDER", "NEEDS CONFIRMATION")


def find_markdown_files() -> list[Path]:
    return sorted(DOCS_DIR.rglob("*.md"))


def check_heading(path: Path, text: str, errors: list[str]) -> None:
    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        errors.append(f"{path.relative_to(DOCS_DIR)}: missing a top-level '# Heading'")


def check_links(path: Path, text: str, errors: list[str]) -> None:
    for match in LINK_RE.finditer(text):
        target = match.group(1)

        if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue

        target_path = target.split("#", 1)[0]
        if not target_path:
            continue

        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(DOCS_DIR)}: broken link -> {target}")


def check_placeholders(path: Path, text: str, warnings: list[str]) -> None:
    for marker in PLACEHOLDER_MARKERS:
        if marker in text:
            warnings.append(f"{path.relative_to(DOCS_DIR)}: contains '{marker}' — needs real content")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    files = find_markdown_files()
    if not files:
        print("No Markdown files found under docs/ — nothing to check.")
        return 0

    for path in files:
        text = path.read_text(encoding="utf-8")
        check_heading(path, text, errors)
        check_links(path, text, errors)
        check_placeholders(path, text, warnings)

    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(files)} files checked, {len(errors)} error(s).")
        return 1

    print(f"{len(files)} files checked, no errors ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
