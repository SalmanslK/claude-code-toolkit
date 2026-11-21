#!/usr/bin/env python3
"""
The mechanical half of /book:check-permissions: the permission catalogue in the code, the plan's
catalogue (authorization §2) and the generated API contracts, set against each other.

    python3 permission_map.py [--root .] [--plan docs/plans/authorization.md]
                              [--contracts docs/api/api-contracts.md] [--catalogue <file>]

It reads three files and writes nothing:

- **The plan's catalogue** — the `| `module` | `action`, ... |` rows of section 2 of the plan.
- **The code's catalogue** — every `const string X = "module.action"` in the catalogue file. The file is the
  one the contracts name ("the catalogue is `<path>`"), or --catalogue.
- **The contracts** — each route's Auth column: `anonymous`, `authenticated`, or the permission(s) its
  request declares. Optional: a stack without generated contracts gets the first comparison only.

It prints the differences, the module → action → routes map, and the routes no permission gates, for the
skill to judge against the FSD. Exit 0 when it ran (findings or none), 2 when the plan or the catalogue
cannot be read. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

PERMISSION = r"[a-z0-9_]+\.[a-z0-9_]+"
PLAN_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|(.+?)\|\s*$", re.M)
CONSTANT = re.compile(r'const\s+string\s+\w+\s*=\s*"(' + PERMISSION + r')"')
CATALOGUE_NAMED = re.compile(r"catalogue is\s+`([^`]+)`")
ROUTE = re.compile(r"^\|\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\|\s*`([^`]+)`\s*\|([^|]*)\|.*\|\s*`?([\w—-]+)`?\s*\|\s*$",
                   re.M)
COUNTS = re.compile(r"(\d+) anonymous, (\d+) authenticated-only, (\d+) permission-gated")


def plan_section_2(text: str) -> str:
    match = re.search(r"^## 2\..*?$(.*?)(?=^## )", text + "\n## end", re.M | re.S)
    return match.group(1) if match else ""


def plan_permissions(text: str) -> set[str]:
    found = set()
    for module, actions in PLAN_ROW.findall(plan_section_2(text)):
        found |= {f"{module}.{action}" for action in re.findall(r"`([a-z0-9_]+)`", actions)}
    return found


def routes(text: str) -> list[tuple[str, str, str, list[str], str]]:
    """(verb, path, kind, permissions, dispatches) per route; kind is anonymous, authenticated or gated."""
    found = []
    for verb, path, auth, dispatches in ROUTE.findall(text):
        permissions = re.findall(r"`(" + PERMISSION + r")`", auth) or re.findall(r"\b(" + PERMISSION + r")\b", auth)
        word = auth.strip().strip("`").lower()
        kind = "gated" if permissions else ("anonymous" if word.startswith("anonymous") else "authenticated")
        found.append((verb, path, kind, permissions, dispatches))
    return found


def report(root: Path, plan: Path, contracts: Path, catalogue: Path | None) -> tuple[list[str], int]:
    lines: list[str] = []
    plan_file = root / plan
    if not plan_file.is_file():
        return [f"BLOCKED: no plan at {plan} — the Book keeps the permission catalogue in authorization §2"], 2
    planned = plan_permissions(plan_file.read_text(encoding="utf-8-sig"))
    if not planned:
        lines.append(f"NOTE: no `module` | `action` rows found in section 2 of {plan}")
    contracts_file = root / contracts
    contracts_text = contracts_file.read_text(encoding="utf-8-sig") if contracts_file.is_file() else ""
    if catalogue is None and contracts_text:
        named = CATALOGUE_NAMED.search(contracts_text)
        catalogue = Path(named.group(1)) if named else None
    if catalogue is None or not (root / catalogue).is_file():
        return lines + ["BLOCKED: the code's permission catalogue was not found; pass --catalogue <file>"], 2
    coded = set(CONSTANT.findall((root / catalogue).read_text(encoding="utf-8-sig")))

    lines.append(f"Plan {plan.as_posix()}: {len(planned)} permissions. Code {catalogue.as_posix()}: {len(coded)}.")
    lines.append("")
    lines.append("## 1. Catalogue: plan §2 against the code")
    for title, items in (("In the code, not in plan §2", coded - planned), ("In plan §2, not in the code", planned - coded)):
        lines.append(f"- {title}: " + (", ".join(sorted(items)) if items else "none"))

    if not contracts_text:
        lines += ["", f"NOTE: no generated contracts at {contracts}; the route comparisons are skipped."]
        return lines, 0
    table = routes(contracts_text)
    used: dict[str, list[str]] = defaultdict(list)
    for verb, path, kind, permissions, dispatches in table:
        for permission in permissions:
            used[permission].append(f"{verb} {path}")
    kinds = {k: [r for r in table if r[2] == k] for k in ("anonymous", "authenticated", "gated")}

    lines += ["", "## 2. Catalogue against the routes"]
    lines.append("- Declared by a route, not in the code's catalogue: "
                 + (", ".join(sorted(set(used) - coded)) or "none"))
    lines.append("- In the catalogue, gating no route: " + (", ".join(sorted(coded - set(used))) or "none"))
    stated = COUNTS.search(contracts_text)
    if stated:
        counted = (len(kinds["anonymous"]), len(kinds["authenticated"]), len(kinds["gated"]))
        same = tuple(int(n) for n in stated.groups()) == counted
        lines.append(f"- Parsed {counted[0]} anonymous, {counted[1]} authenticated-only, {counted[2]} gated; the "
                     f"contracts say {stated.group(0)}" + ("" if same else " — MISMATCH: read the contracts by hand"))

    lines += ["", "## 3. Module → action → routes"]
    modules: dict[str, list[str]] = defaultdict(list)
    for permission in sorted(coded | set(used)):
        modules[permission.split(".")[0]].append(permission)
    for module, permissions in modules.items():
        lines.append(f"- {module}")
        for permission in permissions:
            lines.append(f"  - {permission.split('.', 1)[1]}: " + ("; ".join(used.get(permission, [])) or "no route"))

    for kind, title in (("authenticated", "Routes any signed-in user may call (no permission)"),
                        ("anonymous", "Anonymous routes")):
        lines += ["", f"## {4 if kind == 'authenticated' else 5}. {title}: {len(kinds[kind])}"]
        lines += [f"- {verb} {path} → {dispatches}" for verb, path, _, _, dispatches in kinds[kind]]
    return lines, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--plan", type=Path, default=Path("docs/plans/authorization.md"))
    parser.add_argument("--contracts", type=Path, default=Path("docs/api/api-contracts.md"))
    parser.add_argument("--catalogue", type=Path)
    args = parser.parse_args(argv)
    lines, code = report(args.root, args.plan, args.contracts, args.catalogue)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
