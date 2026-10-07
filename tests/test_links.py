"""Fail when a markdown file links to a relative path that does not exist.

Run with `pytest tests/` or `python tests/test_links.py`.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
SKIP_DIRS = {".git", ".scratch"}


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def broken_links():
    for path in markdown_files():
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).exists():
                yield f"{path.relative_to(ROOT)} -> {target}"


def test_relative_links_resolve():
    broken = list(broken_links())
    assert not broken, "broken relative links:\n" + "\n".join(broken)


if __name__ == "__main__":
    broken = list(broken_links())
    print("\n".join(broken) or "all relative links resolve")
    raise SystemExit(1 if broken else 0)
