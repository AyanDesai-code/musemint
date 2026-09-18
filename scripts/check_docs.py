#!/usr/bin/env python3
"""Check tracked Markdown hygiene and inline relative file links using stdlib only."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
# Deliberately limited to simple inline links, not a full Markdown parser.
LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")


def check_file(path: Path) -> list[str]:
    errors = []
    name = path.relative_to(ROOT)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"{name}: cannot read UTF-8 Markdown: {exc}"]
    if not text.strip():
        errors.append(f"{name}: empty Markdown file")
    if not text.endswith("\n"):
        errors.append(f"{name}: missing final newline")

    in_fence = False
    fence_char = ""
    fence_length = 0
    for number, line in enumerate(text.splitlines(), 1):
        location = f"{name}:{number}"
        trailing = line[len(line.rstrip()):]
        if trailing:
            errors.append(f"{location}: trailing whitespace")
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_char, fence_length = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                in_fence = False
            continue
        if in_fence:
            continue
        for target in LINK.findall(line):
            try:
                url = urlsplit(target.strip("<>"))
            except ValueError:
                errors.append(f"{location}: malformed link: {target}")
                continue
            if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
                continue
            if not (path.parent / unquote(url.path)).exists():
                errors.append(f"{location}: missing relative link target: {target}")
    return errors


def main() -> int:
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.md"], cwd=ROOT
    ).decode("utf-8").split("\0")
    paths = [ROOT / name for name in tracked if name]
    errors = [error for path in paths for error in check_file(path)]
    if not paths:
        errors.append("No tracked Markdown files found")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Documentation checks passed ({len(paths)} Markdown files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
