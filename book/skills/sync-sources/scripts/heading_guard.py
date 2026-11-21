"""Prove that no markdown heading was renamed or removed since a git ref.

Usage:
    python heading_guard.py [--since HEAD] [--claims] [paths...]

Compares every heading in the working-tree copy of each changed .md file with
the same file at --since. A heading that disappeared is an anchor that inbound
links may still use — check-book.py catches the links that break today, this
catches the heading change itself, so a deliberate rename is a decision rather
than an accident. New headings are fine and are not reported.

--claims also proves that every id (D12, Q4, PROJ-310, FSD-ACCEPT-R01), link
target and number in the changed files survived, counted across all of them
together, so a passage moved or merged from one changed file into another is not
a loss. It cannot tell that a reworded sentence still means the same: a passage
whose claim changed is still read by a person.

Exits 1 if any heading (or, with --claims, any id, link target or number) was lost.
"""
import argparse
import re
import subprocess
import sys
from collections import Counter

HEADING = re.compile(r"^#{1,6}\s+.*$", re.M)
CLAIMS = {
    "id": re.compile(r"\b(?:[DQ]\d+|[A-Z][A-Z0-9]{1,9}-\d+|FSD-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b"),
    "link": re.compile(r"\]\(([^)\s]+)\)"),
    "number": re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?![\w])"),
}


def headings(text: str) -> list:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return [h.strip() for h in HEADING.findall(text)]


def claims(text: str) -> Counter:
    """Every id, link target and number in a text, as (kind, token) counts."""
    found = Counter()
    for kind, pattern in CLAIMS.items():
        found.update((kind, token) for token in pattern.findall(text))
    return found


def lost_claims(before: dict, after: dict) -> list:
    """
    (kind, token, times lost, the files it was in) for each claim the changed files held before and
    hold fewer times after, all files counted together. `after` lacks a file that was deleted.
    """
    was, now, where = Counter(), Counter(), {}
    for path, text in before.items():
        for claim, n in claims(text).items():
            was[claim] += n
            where.setdefault(claim, []).append(path)
    for text in after.values():
        now.update(claims(text))
    return [(kind, token, n, where[(kind, token)]) for (kind, token), n in sorted((was - now).items())]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default="HEAD")
    parser.add_argument("--claims", action="store_true", help="also ids, link targets and numbers")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    changed = args.paths or subprocess.run(
        ["git", "diff", "--name-only", args.since, "--", "*.md"],
        capture_output=True, text=True, encoding="utf-8").stdout.split()

    sys.stdout.reconfigure(encoding="utf-8")
    lost = 0
    before_texts, after_texts = {}, {}
    for path in changed:
        before = subprocess.run(["git", "show", f"{args.since}:{path}"], capture_output=True, text=True, encoding="utf-8")
        try:
            after = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            after = None
        if after is not None:
            after_texts[path] = after
        if before.returncode != 0:
            continue  # new file
        before_texts[path] = before.stdout
        if after is None:
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
    if args.claims:
        gone = lost_claims(before_texts, after_texts)
        for kind, token, n, paths in gone:
            print(f"LOST {kind}  {token}  x{n}  (was in {', '.join(paths)})")
        print(f"{sum(n for _, _, n, _ in gone)} ids, link targets and numbers lost")
        lost += len(gone)
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main())
