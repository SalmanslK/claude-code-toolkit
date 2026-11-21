#!/usr/bin/env python3
"""The next free defect (D<n>) and question (Q<n>) id, across every branch.

    python "${CLAUDE_SKILL_DIR}/scripts/next_id.py" [REPO_ROOT]

The project is REPO_ROOT, or else the git top level of the current directory. The ledgers are read with
that project's devtools/checks/ledger_ids.py; a project without it stops this with exit 2.

Ids are never reused, and two branches that each take "the next number" collide (docs/CLAUDE.md, Ids).
So the highest id is looked for on the base (`base_ref` in devtools/factory/factory.toml), on every
local and remote-tracking branch, and in the working tree: in docs/defects.md and docs/open-questions.md
and their archives. A defect is a ledger row or a *Fixed* entry; a question is a `#### Q<n>` section.

Prints the next D and Q, and where the highest of each was seen. A base that is not fetched stops it with
exit 2: a next id read without the base could be one the base already holds.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

LEDGERS = {"D": ("docs/defects.md", "docs/archive/defects-closed.md"),
           "Q": ("docs/open-questions.md", "docs/archive/questions-resolved.md")}
WORKING_TREE = "working tree"


class CouldNotCheck(Exception):
    pass


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
    except OSError as error:
        raise CouldNotCheck(f"git could not run ({error})") from error


def project_root(given: str | None) -> Path:
    """REPO_ROOT if given, else the git top level of the current directory."""
    if given:
        return Path(given).resolve()
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError as error:
        raise CouldNotCheck(f"git could not run ({error})") from error
    if done.returncode != 0 or not done.stdout.strip():
        raise CouldNotCheck("the current directory is not inside a git repository: run it from the project")
    return Path(done.stdout.strip()).resolve()


def ledger_ids(root: Path):
    """The project's own devtools/checks/ledger_ids.py, the one reader of the ledgers."""
    path = root / "devtools" / "checks" / "ledger_ids.py"
    if not path.is_file():
        raise CouldNotCheck(f"{root} has no devtools/checks/ledger_ids.py: it is not a Book, or an older one")
    spec = importlib.util.spec_from_file_location("ledger_ids", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # a dataclass looks its module up there
    spec.loader.exec_module(module)
    return module


def ids_in(kind: str, text: str, ledger) -> set[int]:
    patterns = (ledger.DEFECT_ROW, ledger.FIXED_ENTRY) if kind == "D" else (ledger.QUESTION_HEADING,)
    return {int(found[1:]) for pattern in patterns for found in pattern.findall(text)}


def base_ref(root: Path) -> str:
    path = root / "devtools" / "factory" / "factory.toml"
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except tomllib.TOMLDecodeError as error:
        raise CouldNotCheck(f"devtools/factory/factory.toml is not valid TOML ({error})") from error
    if not config.get("base_ref"):
        raise CouldNotCheck("devtools/factory/factory.toml sets no base_ref: the branch ids are taken against")
    return str(config["base_ref"])


def refs(root: Path, base: str) -> list[str]:
    if git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
        raise CouldNotCheck(f"{base} is not here: fetch it first (`git fetch`)")
    # Full names, so a remote's HEAD (`refs/remotes/origin/HEAD`, short name `origin`) is plain to skip.
    listed = git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes")
    short = [ref.split("/", 2)[2] for ref in listed.stdout.split() if not ref.endswith("/HEAD")]
    others = [ref for ref in short if ref != base]
    return [base, *others]


def highest(root: Path) -> dict[str, tuple[int, str]]:
    """{kind: (highest id number, where it was seen)}."""
    ledger = ledger_ids(root)
    base = base_ref(root)
    found = {kind: (0, base) for kind in LEDGERS}
    sources = [(ref, lambda path, ref=ref: git(root, "show", f"{ref}:{path}").stdout) for ref in refs(root, base)]
    sources.append((WORKING_TREE, lambda path: (root / path).read_text(encoding="utf-8", errors="replace")
                    if (root / path).is_file() else ""))
    for where, read in sources:
        for kind, paths in LEDGERS.items():
            top = max(ids_in(kind, "\n".join(read(path) for path in paths), ledger), default=0)
            if top > found[kind][0]:
                found[kind] = (top, where)
    return found


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        found = highest(project_root(args[0] if args else None))
    except CouldNotCheck as error:
        print(f"next_id: could not check — {error}", file=sys.stderr)
        return 2
    for kind, (top, where) in found.items():
        print(f"next {kind}: {kind}{top + 1}" + (f"  (highest {kind}{top}, on {where})" if top else "  (none taken yet)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
