"""Check every internal markdown link and anchor in the living docs.

Usage:
    python linkcheck.py [REPO_ROOT] [--files a.md b.md ...]

With no --files, checks docs/**/*.md (except docs/archive/) plus CLAUDE.md,
README.md, AI-DEVELOPMENT-GUIDE.md and AGENTS.md. Anchors follow GitHub's
slug rules: lowercase, punctuation other than hyphens and spaces dropped,
spaces to hyphens, so "Q60 · What counts…" becomes "q60--what-counts". A
repeated heading gets -1, -2 suffixes; <a id="..."> / <a name="..."> also count.

Exits 1 when anything is broken, so it can gate a commit.
"""
import argparse
import glob
import os
import re
import sys

ROOT_FILES = ("CLAUDE.md", "README.md", "AI-DEVELOPMENT-GUIDE.md", "AGENTS.md")


def slug(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[`*_~\[\]()]", "", text)
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(path: str) -> set:
    found, seen, in_fence = set(), {}, False
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            match = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
            if match:
                base = slug(match.group(1))
                count = seen.get(base, 0)
                found.add(base if count == 0 else f"{base}-{count}")
                seen[base] = count + 1
            found.update(re.findall(r'<a (?:name|id)="([^"]+)"', line))
    return found


def default_files(root: str) -> list:
    docs = [
        f for f in glob.glob(os.path.join(root, "docs", "**", "*.md"), recursive=True)
        if os.sep + "archive" + os.sep not in f
    ]
    return docs + [os.path.join(root, name) for name in ROOT_FILES if os.path.exists(os.path.join(root, name))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--files", nargs="*")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    files = [os.path.abspath(f) for f in args.files] if args.files else default_files(root)

    cache, checked, broken = {}, 0, 0
    for source in files:
        text = open(source, encoding="utf-8", errors="replace").read()
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for match in re.finditer(r"\]\(([^)\s]+)\)", text):
            target = match.group(1)
            if re.match(r"^(https?:|mailto:)", target):
                continue
            path, _, fragment = target.partition("#")
            resolved = os.path.normpath(os.path.join(os.path.dirname(source), path)) if path else source
            checked += 1
            where = os.path.relpath(source, root)
            if not os.path.exists(resolved):
                broken += 1
                print(f"MISSING  {where}  {target}")
                continue
            if fragment and resolved.endswith(".md"):
                if resolved not in cache:
                    cache[resolved] = anchors_of(resolved)
                if fragment not in cache[resolved]:
                    broken += 1
                    print(f"ANCHOR   {where}  {target}")
    print(f"checked {checked} broken {broken}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
