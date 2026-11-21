"""Cross-check question (Q<n>) and defect (D<n>) status across the docs.

Usage:
    python "${CLAUDE_SKILL_DIR}/scripts/id_status.py" [REPO_ROOT]

The project is REPO_ROOT, or else the git top level of the current directory. The ledgers are read with
that project's devtools/checks/ledger_ids.py; a project without it stops this with exit 2.

Reads the owners:
  docs/open-questions.md - Q ids with a `#### Q<n> —` (or `·`) section between "## Still open"
                           and "## Superseded" are open; every other Q section there,
                           and every one in docs/archive/questions-resolved.md, is closed.
  docs/defects.md        - D ids in the "## Open" tables are open; a fixed defect is a one-line
                           entry under "## Fixed" (`- **D21** — …`), and its full row is in
                           docs/archive/defects-closed.md: those ids are closed.

A heading it relies on that is missing stops it with exit 1: an empty slice would
report every check clean while checking nothing.

Then prints:
  1. Still-open summary-table rows vs the `#### Q` sections below them,
  2. candidate stale citations in every other living doc: a CLOSED id whose
     own words call it open, or an OPEN id whose own words call it closed.
     "Its own words" = the text between it and the neighbouring ids on the
     line, so "Q94 (answered) … Q123 open" flags neither.

Section 2 is a candidate list, not a verdict: history lines ("was open until…")
legitimately match. It exists so an agent reads twenty lines, not 37k.

The ledgers are read by devtools/checks/ledger_ids.py, shared with /book:check-guides.

Duplicate D and Q ids are not this script's: devtools/checks/check-book.py fails
pre-commit and CI on them.
"""
import glob
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = ("archive", "release-notes", "Audit")


def read(root: str, *parts: str) -> str:
    path = os.path.join(root, *parts)
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def project_root(given: str | None) -> str | None:
    """REPO_ROOT if given, else the git top level of the current directory; None if there is none."""
    if given:
        return os.path.abspath(given)
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError:
        return None
    return os.path.abspath(done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else None


def ledger_ids(root: str):
    """The project's own devtools/checks/ledger_ids.py, shared with /book:check-guides: one reader, no copy."""
    path = Path(root) / "devtools" / "checks" / "ledger_ids.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ledger_ids", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # a dataclass looks its module up there
    spec.loader.exec_module(module)
    return module


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    root = project_root(sys.argv[1] if len(sys.argv) > 1 else None)
    if root is None:
        print("id_status: could not check — the current directory is not inside a git repository", file=sys.stderr)
        return 2
    ledger = ledger_ids(root)
    if ledger is None:
        print(f"id_status: could not check — {root} has no devtools/checks/ledger_ids.py", file=sys.stderr)
        return 2
    FIXED_ENTRY, ID, LedgerMissing = ledger.FIXED_ENTRY, ledger.ID, ledger.LedgerMissing
    try:
        ledgers = ledger.Ledgers.read(read(root, "docs", "open-questions.md"),
                               read(root, "docs", "archive", "questions-resolved.md"),
                               read(root, "docs", "defects.md"),
                               read(root, "docs", "archive", "defects-closed.md"))
    except LedgerMissing as error:
        raise SystemExit(f"id_status: {error} — could not check; nothing below would mean anything.")
    open_q = ledgers.ids("Q", open_=True)

    print("== 1. Still-open summary rows vs sections")
    print(f"  rows without a section: {sorted(ledgers.open_rows - open_q) or 'none'}")
    print(f"  sections without a row: {sorted(open_q - ledgers.open_rows) or 'none'}")

    print("== 2. candidate stale citations (read each before changing)")
    files = [f for f in glob.glob(os.path.join(root, "docs", "**", "*.md"), recursive=True)
             if not any(os.sep + d + os.sep in f for d in SKIP_DIRS)]
    files += [os.path.join(root, n) for n in ("CLAUDE.md", "README.md") if os.path.exists(os.path.join(root, n))]
    hits = 0
    for path in files:
        for number, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
            if (line.lstrip().startswith("#### ") or re.match(r"^\|\s*\*\*D\d+\*\*", line)
                    or (os.path.basename(path) == "defects.md" and FIXED_ENTRY.match(line))):
                continue  # a question's own heading, or a defect's own row or Fixed entry
            for match in ID.finditer(line):
                ident = match.group(1)
                status = ledgers.status.get(ident)
                if status is None:
                    continue
                words = ledger.own_words(line, match)
                flag = ledger.citation_flag(status, words)
                if flag:
                    hits += 1
                    print(f"  {os.path.relpath(path, root)}:{number}  {ident}  {flag}: …{words.strip()}…")
    print(f"  {hits} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
