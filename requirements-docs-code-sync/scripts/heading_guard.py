"""Prove that no markdown heading was renamed or removed since a git ref.

Usage:
    python heading_guard.py [--since HEAD] [paths...]

Compares every heading in the working-tree copy of each changed .md file with
the same file at --since. A heading that disappeared is an anchor that inbound
links may still use — linkcheck.py catches the links that break today, this
catches the heading change itself, so a deliberate rename is a decision rather
than an accident. New headings are fine and are not reported.

Exits 1 if any heading was lost.
"""
import argparse
import re
import subprocess
import sys

HEADING = re.compile(r"^#{1,6}\s+.*$", re.M)


def headings(text: str) -> list:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return [h.strip() for h in HEADING.findall(text)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default="HEAD")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    changed = args.paths or subprocess.run(
        ["git", "diff", "--name-only", args.since, "--", "*.md"],
        capture_output=True, text=True, encoding="utf-8").stdout.split()

    sys.stdout.reconfigure(encoding="utf-8")
    lost = 0
    for path in changed:
        before = subprocess.run(["git", "show", f"{args.since}:{path}"], capture_output=True, text=True, encoding="utf-8")
        if before.returncode != 0:
            continue  # new file
        try:
            after = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"DELETED FILE  {path}")
            lost += 1
            continue
        remaining = headings(after)
        for heading in headings(before.stdout):
            if heading in remaining:
                remaining.remove(heading)
            else:
                lost += 1
                print(f"LOST  {path}  {heading}")
    print(f"{len(changed)} files checked, {lost} headings lost")
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main())
