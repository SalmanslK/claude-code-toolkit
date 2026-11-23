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
import re
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
    loader_path = root / "devtools" / "factory" / "book_config.py"
    if loader_path.is_file():
        # A Book from 1.6 keeps only its own values in factory.toml; its loader merges the Book's defaults under it.
        spec = importlib.util.spec_from_file_location("book_config", loader_path)
        loader = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(loader)
            config = loader.load(root)
        except Exception as error:  # a loader that does not run cannot say where the base is
            raise CouldNotCheck(f"the project's settings do not load ({error})") from error
        if not config.get("base_ref"):
            raise CouldNotCheck("the settings set no base_ref: the branch ids are taken against it")
        return str(config["base_ref"])
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except tomllib.TOMLDecodeError as error:
        raise CouldNotCheck(f"devtools/factory/factory.toml is not valid TOML ({error})") from error
    if not config.get("base_ref"):
        raise CouldNotCheck("devtools/factory/factory.toml sets no base_ref: the branch ids are taken against")
    return str(config["base_ref"])


def refs(root: Path, base: str) -> list[tuple[str, str]]:
    """(full ref name, short name) for the base and every other branch, local or remote. Ledgers are read by the
    full name: a short name that is also a tag's would read the tag (Book D58)."""
    if git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
        raise CouldNotCheck(f"{base} is not here: fetch it first (`git fetch`)")
    full_base = git(root, "rev-parse", "--symbolic-full-name", base).stdout.strip() or base
    # Full names, so a remote's HEAD (`refs/remotes/origin/HEAD`, short name `origin`) is plain to skip.
    listed = git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes")
    others = [(ref, ref.split("/", 2)[2]) for ref in listed.stdout.split()
              if not ref.endswith("/HEAD") and ref != full_base]
    return [(full_base, base), *others]


def read_blobs(root: Path, specs: list[str]) -> dict[str, str]:
    """{"<ref>:<path>": text} for each spec that names a file, in two git calls whatever the branch count.

    One `git cat-file --batch-check` names each spec's blob; one `git cat-file --batch` reads each distinct
    blob once. A spec that names no file is left out. (One `git show` per branch and file took minutes on a
    repository with some hundreds of branches.)"""
    try:
        checked = subprocess.run(["git", "-C", str(root), "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                                 input="".join(spec + "\n" for spec in specs).encode("utf-8"), capture_output=True)
    except OSError as error:
        raise CouldNotCheck(f"git could not run ({error})") from error
    if checked.returncode != 0:
        raise CouldNotCheck("git cat-file --batch-check failed: " + checked.stderr.decode("utf-8", "replace").strip())
    blob_of: dict[str, str] = {}
    for spec, line in zip(specs, checked.stdout.decode("utf-8", "replace").splitlines()):
        parts = line.split()
        if len(parts) == 2 and parts[1] == "blob":
            blob_of[spec] = parts[0]
    distinct = sorted(set(blob_of.values()))
    if not distinct:
        return {}
    try:
        batch = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
                               input="".join(oid + "\n" for oid in distinct).encode("ascii"), capture_output=True)
    except OSError as error:
        raise CouldNotCheck(f"git could not run ({error})") from error
    if batch.returncode != 0:
        raise CouldNotCheck("git cat-file --batch failed: " + batch.stderr.decode("utf-8", "replace").strip())
    texts: dict[str, str] = {}
    data, at = batch.stdout, 0
    while at < len(data):  # each object: "<oid> <type> <size>\n<content>\n"
        header_end = data.index(b"\n", at)
        oid, _, size = data[at:header_end].decode("ascii").split()
        start = header_end + 1
        texts[oid] = data[start:start + int(size)].decode("utf-8", errors="replace")
        at = start + int(size) + 1
    return {spec: texts.get(oid, "") for spec, oid in blob_of.items()}


def highest(root: Path) -> dict[str, tuple[int, str]]:
    """{kind: (highest id number, where it was seen)}."""
    ledger = ledger_ids(root)
    base = base_ref(root)
    found = {kind: (0, base) for kind in LEDGERS}
    branches = refs(root, base)
    every_path = [path for paths in LEDGERS.values() for path in paths]
    blobs = read_blobs(root, [f"{ref}:{path}" for ref, _ in branches for path in every_path])
    sources = [(name, lambda path, ref=ref: blobs.get(f"{ref}:{path}", "")) for ref, name in branches]
    sources.append((WORKING_TREE, lambda path: (root / path).read_text(encoding="utf-8", errors="replace")
                    if (root / path).is_file() else ""))
    for kind, paths in LEDGERS.items():
        texts = [(where, "\n".join(read(path) for path in paths)) for where, read in sources]
        top = highest_in(kind, {text for _, text in texts}, ledger)
        if top:
            # The first source holding it, in order: the base, the branches, the working tree.
            found[kind] = (top[0], next(where for where, text in texts if top[1].get(text) == top[0]))
    return found


def highest_in(kind: str, texts: set[str], ledger) -> tuple[int, dict[str, int]] | None:
    """(the highest id in any of the texts, {text: its highest} for the texts that were parsed), or None.

    Parsing every branch's ledger is the slow part, so the texts are taken in order of a cheap upper bound
    (the largest `D<n>`/`Q<n>` anywhere in them) and parsing stops once no bound can beat the best found."""
    loose = re.compile(kind + r"(\d+)")
    bounds = sorted(((max((int(n) for n in loose.findall(text)), default=0), text) for text in texts),
                    key=lambda pair: pair[0], reverse=True)
    best, parsed = 0, {}
    for bound, text in bounds:
        if bound < best or bound == 0:
            break
        parsed[text] = max(ids_in(kind, text, ledger), default=0)
        best = max(best, parsed[text])
    return (best, parsed) if best else None


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
