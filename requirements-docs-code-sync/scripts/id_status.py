"""Cross-check question (Q<n>) and defect (D<n>) status across the docs.

Usage:
    python id_status.py [REPO_ROOT]

Reads the owners:
  docs/project.md  - Q ids with a `#### Q<n> ·` section between "## Still open"
                     and "## Superseded" are open; every other Q section is closed.
  docs/defects.md  - D ids in the "## Open" table are open; the rest are closed.

Then prints:
  1. duplicate defect ids (one id on two different rows),
  2. Still-open summary-table rows vs the `#### Q` sections below them,
  3. candidate stale citations in every other living doc: a CLOSED id whose
     own words call it open, or an OPEN id whose own words call it closed.
     "Its own words" = the text between it and the neighbouring ids on the
     line, so "Q94 (answered) … Q123 open" flags neither.

Section 3 is a candidate list, not a verdict: history lines ("was open until…")
legitimately match. It exists so an agent reads twenty lines, not 37k.
"""
import glob
import os
import re
import sys

OPENISH = re.compile(r"still open|stays open|unanswered|not yet answered|pending an answer|remains open|\bis open\b|\(open\)|, open\b", re.I)
CLOSEDISH = re.compile(r"answered|closed|resolved|fixed|superseded|confirmed|reversed", re.I)
ID = re.compile(r"\b([QD]\d{1,3})\b")
SKIP_DIRS = ("archive", "release-notes", "Audit")


NEGATED = re.compile(r"\b(?:not|until|un)\b[^.|;]{0,25}?(?:answered|fixed|resolved|closed)", re.I)


def own_words(line: str, match: re.Match) -> str:
    """What the line says about this id: a little before it, and the clause after it.

    Status words usually follow the id ("[D136] open", "Q94 … still open") or sit
    just before it ("superseded by Q44"), so take 25 characters before and the
    rest of the clause after, stopping at the next id or a clause break. A
    negated closing word ("not fixed", "until … is answered") counts as open.
    """
    before = ID.split(line[:match.start()])[-1][-25:]
    after = re.split(r"[.;|]", ID.split(line[match.end():])[0], maxsplit=1)[0][:80]
    return NEGATED.sub(" still open ", before + match.group(1) + after)


def main() -> int:
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    project = open(os.path.join(root, "docs", "project.md"), encoding="utf-8").read()
    defects = open(os.path.join(root, "docs", "defects.md"), encoding="utf-8").read()
    sys.stdout.reconfigure(encoding="utf-8")

    still_open = project[project.find("\n## Still open"):project.find("\n## Superseded")]
    open_q = set(re.findall(r"^#### (Q\d+) ·", still_open, re.M))
    summary = still_open.split("\n#### ", 1)[0]  # the first table only
    open_rows = set(re.findall(r"^\| (?:⛔ )?\[(Q\d+)\]\(", summary, re.M))
    closed_q = set(re.findall(r"^#### (Q\d+) ·", project, re.M)) - open_q

    open_block = defects[defects.find("\n## Open"):defects.find("\n## Fixed")]
    open_d = set(re.findall(r"^\|\s*\*\*(D\d+)\*\*", open_block, re.M))
    rows = re.findall(r"^\|\s*\*\*(D\d+)\*\*", defects, re.M)
    closed_d = set(rows) - open_d

    print("== 1. duplicate defect ids")
    dups = sorted({d for d in rows if rows.count(d) > 1}, key=lambda d: int(d[1:]))
    print("  " + (", ".join(dups) if dups else "none"))

    print("== 2. Still-open summary rows vs sections")
    print(f"  rows without a section: {sorted(open_rows - open_q) or 'none'}")
    print(f"  sections without a row: {sorted(open_q - open_rows) or 'none'}")

    print("== 3. candidate stale citations (read each before changing)")
    files = [f for f in glob.glob(os.path.join(root, "docs", "**", "*.md"), recursive=True)
             if not any(os.sep + d + os.sep in f for d in SKIP_DIRS)]
    files += [os.path.join(root, n) for n in ("CLAUDE.md", "README.md") if os.path.exists(os.path.join(root, n))]
    hits = 0
    for path in files:
        for number, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
            if line.lstrip().startswith("#### ") or re.match(r"^\|\s*\*\*D\d+\*\*", line):
                continue  # a question's own heading, or a defect's own row
            for match in ID.finditer(line):
                ident, words = match.group(1), own_words(line, match)
                is_open, is_closed = OPENISH.search(words), CLOSEDISH.search(words)
                flag = None
                if (ident in closed_q or ident in closed_d) and is_open and not is_closed:
                    flag = "closed, cited as open"
                elif (ident in open_q or ident in open_d) and is_closed and not is_open:
                    flag = "open, cited as closed"
                if flag:
                    hits += 1
                    print(f"  {os.path.relpath(path, root)}:{number}  {ident}  {flag}: …{words.strip()}…")
    print(f"  {hits} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
