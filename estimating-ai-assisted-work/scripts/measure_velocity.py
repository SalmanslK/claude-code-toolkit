#!/usr/bin/env python3
"""Measure a team's delivery velocity from git history.

Prints active developer-days, the date span, merged pull requests, the share of
fix commits and, when --modules is given, hours per module (H): the one number
the estimating skill scales every unit cost from.

Standard library only. Read-only: runs `git log` and nothing else.

Examples:
  python measure_velocity.py --repo /path/to/repo
  python measure_velocity.py --repo . --branch develop --paths src tests --modules 30
  python measure_velocity.py --repo . --since 2026-01-01 --until 2026-03-31 --json
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys

DEFAULT_BRANCH_CANDIDATES = ("dev", "develop", "development", "main", "master", "trunk")
DEFAULT_CODE_DIRS = ("src", "app", "apps", "lib", "libs", "packages", "services", "server",
                     "client", "backend", "frontend", "mobile", "tests", "test", "spec")
MERGE_SUBJECT = re.compile(r"^(Merged in |Merge pull request |Merged PR )", re.I)
FEATURE_MERGE = re.compile(r"(feature|feat)[/-]", re.I)
FIX_SUBJECT = re.compile(r"\b(fix(es|ed)?|bug|defect|hotfix|regression|revert)\b", re.I)
BOT_NAME = re.compile(r"(\[bot\]|\bbot\b|dependabot|renovate|github-actions)", re.I)


def git(repo: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def ref_exists(repo: str, ref: str) -> bool:
    return subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", ref],
                          capture_output=True).returncode == 0


def detect_branch(repo: str) -> str:
    head = subprocess.run(["git", "-C", repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"],
                          capture_output=True, text=True)
    integration = [f"origin/{n}" for n in DEFAULT_BRANCH_CANDIDATES[:3]] + list(DEFAULT_BRANCH_CANDIDATES[:3])
    # Prefer an integration branch (dev/develop) over main: it carries the work as it lands.
    for ref in integration:
        if ref_exists(repo, ref):
            return ref
    if head.returncode == 0 and head.stdout.strip():
        return head.stdout.strip().replace("refs/remotes/", "")
    for name in DEFAULT_BRANCH_CANDIDATES[3:]:
        for ref in (f"origin/{name}", name):
            if ref_exists(repo, ref):
                return ref
    return "HEAD"


def detect_paths(repo: str) -> list[str]:
    found = [d for d in DEFAULT_CODE_DIRS if os.path.isdir(os.path.join(repo, d))]
    return found  # empty list means the whole repository


def normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".")
    p.add_argument("--branch", help="integration branch; auto-detected if omitted")
    p.add_argument("--paths", nargs="*", help="code folders; auto-detected if omitted, whole repo if none found")
    p.add_argument("--since", help="YYYY-MM-DD")
    p.add_argument("--until", help="YYYY-MM-DD")
    p.add_argument("--hours-per-day", type=float, default=8.0)
    p.add_argument("--overhead", type=float, default=0.15,
                   help="share added for design/fix days with no commit (default 0.15)")
    p.add_argument("--modules", type=int, help="modules shipped in the window; gives hours per module (H)")
    p.add_argument("--alias", action="append", default=[],
                   help="merge two author names: 'Name One=Name Two' (repeatable)")
    p.add_argument("--exclude-author", action="append", default=[],
                   help="leave out an author who is not on the team (repeatable; matches part of the name)")
    p.add_argument("--team-size", help="declared team size over time, 'YYYY-MM-DD:FTE,...' (e.g. 2026-08-27:1,2026-08-31:2,2026-09-07:2.5). "
                   "Caps each week's commit-days at FTE x working days, on THESE commit-days, and prints the capped H. "
                   "Use this H for pricing; never multiply an uncapped H by a cap factor measured on another day set.")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    repo = os.path.abspath(a.repo)
    branch = a.branch or detect_branch(repo)
    paths = a.paths if a.paths is not None else detect_paths(repo)
    window = ([f"--since={a.since}"] if a.since else []) + ([f"--until={a.until} 23:59"] if a.until else [])

    aliases = {}
    for pair in a.alias:
        left, _, right = pair.partition("=")
        aliases[normalise(left)] = normalise(right)

    log = git(repo, "log", branch, "--no-merges", "--format=%an\x1f%ad\x1f%s", "--date=short",
              *window, "--", *paths)
    author_days: set[tuple[str, str]] = set()
    display: dict[str, str] = {}
    commits = fixes = 0
    dates: list[str] = []
    seen_days: set[tuple[str, str]] = set()
    weekly: dict[str, set[str]] = collections.defaultdict(set)
    monthly: collections.Counter[str] = collections.Counter()
    for line in log.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        name, date, subject = parts
        if BOT_NAME.search(name):
            continue
        key = normalise(name)
        key = aliases.get(key, key)
        if any(normalise(x) and normalise(x) in key for x in a.exclude_author):
            continue
        display.setdefault(key, name.rstrip("*").strip())
        author_days.add((key, date))
        commits += 1
        fixes += bool(FIX_SUBJECT.search(subject))
        dates.append(date)
        iso = datetime.date.fromisoformat(date).isocalendar()
        weekly[f"{iso[0]}-W{iso[1]:02d}"].add(key)
        if (key, date) not in seen_days:
            seen_days.add((key, date))
            monthly[date[:7]] += 1

    if not dates:
        sys.exit(f"No commits found on {branch} for paths {paths or ['(whole repo)']} in the window.")

    merges = git(repo, "log", branch, "--merges", "--format=%s", *window).splitlines()
    prs = [m for m in merges if MERGE_SUBJECT.search(m)]
    feature_prs = [m for m in prs if FEATURE_MERGE.search(m)]

    per_author = collections.Counter(k for k, _ in author_days)
    active_days = len(author_days)
    hours = active_days * a.hours_per_day * (1 + a.overhead)
    capped_days = None
    if a.team_size:
        sched = sorted((datetime.date.fromisoformat(x.split(":")[0]), float(x.split(":")[1])) for x in a.team_size.split(","))
        since_d = datetime.date.fromisoformat(a.since) if a.since else min(datetime.date.fromisoformat(d) for _, d in author_days)
        until_d = datetime.date.fromisoformat(a.until) if a.until else None
        per_week: collections.Counter = collections.Counter()
        for _, d in author_days:
            dd = datetime.date.fromisoformat(d)
            per_week[dd - datetime.timedelta(days=dd.weekday())] += 1
        capped_days = 0.0
        for wk, n in per_week.items():
            work = sum(1 for i in range(5) if since_d <= wk + datetime.timedelta(days=i) and (until_d is None or wk + datetime.timedelta(days=i) <= until_d))
            fte = None
            for d0, f0 in sched:
                if d0 <= wk + datetime.timedelta(days=4):
                    fte = f0
            capped_days += n * (min(1.0, fte * work / n) if fte else 1.0)
        capped_hours = capped_days * a.hours_per_day * (1 + a.overhead)
    devs_per_week = [len(v) for v in weekly.values()]
    result = {
        "repo": os.path.basename(repo),
        "branch": branch,
        "paths": paths or ["(whole repository)"],
        "first_commit": min(dates),
        "last_commit": max(dates),
        "weeks_with_commits": len(weekly),
        "avg_active_developers_per_week": round(sum(devs_per_week) / len(devs_per_week), 1),
        "active_developer_days": active_days,
        "per_author_active_days": {display[k]: v for k, v in per_author.most_common()},
        "non_merge_commits": commits,
        "fix_commit_share": round(fixes / commits, 2),
        "merged_pull_requests": len(prs),
        "merged_feature_pull_requests": len(feature_prs),
        "hours_per_day": a.hours_per_day,
        "overhead": a.overhead,
        "estimated_delivery_hours": round(hours),
        "active_days_per_month": dict(sorted(monthly.items())),
        "modules": a.modules,
        "hours_per_module_H": round(hours / a.modules, 1) if a.modules else None,
    }
    if capped_days is not None:
        result["capped_active_developer_days"] = round(capped_days, 1)
        result["capped_hours"] = round(capped_hours)
        result["hours_per_module_H_capped"] = round(capped_hours / a.modules, 1) if a.modules else None

    if a.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Repository   {result['repo']}  branch {branch}  paths {', '.join(result['paths'])}")
    stale_days = (datetime.date.today() - datetime.date.fromisoformat(result["last_commit"])).days
    print(f"Window       {result['first_commit']} -> {result['last_commit']}  "
          f"({result['weeks_with_commits']} weeks with commits, "
          f"~{result['avg_active_developers_per_week']} active developers/week)")
    if stale_days > 28:
        print(f"Freshness    last commit is {stale_days} days old: ask whether recent work lives elsewhere"
              " (or fetch, if allowed).")
    print("Active developer-days per author:")
    for who, days in result["per_author_active_days"].items():
        print(f"  {days:4d}  {who}")
    print("Active developer-days per month (gaps and setup months show here):")
    first, last = min(monthly), max(monthly)
    y, m = int(first[:4]), int(first[5:])
    while f"{y}-{m:02d}" <= last:
        key = f"{y}-{m:02d}"
        print(f"  {key}  {monthly.get(key, 0):4d}  {'#' * min(monthly.get(key, 0), 60)}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    print(f"Total        {active_days} active developer-days "
          f"x {a.hours_per_day:g}h x {1 + a.overhead:g} = ~{result['estimated_delivery_hours']}h")
    print(f"Assumes      a day counts only if it has a commit; the {a.overhead:.0%} overhead stands in for"
          " design, review and QA days with none. Raise --overhead if the team commits rarely.")
    print(f"Commits     {commits} non-merge, {result['fix_commit_share']:.0%} fix/defect/revert")
    print(f"Merged PRs   {len(prs)} ({len(feature_prs)} from feature branches)")
    if a.modules:
        print(f"H            {result['hours_per_module_H']}h per module ({a.modules} modules)")
        if capped_days is not None:
            print(f"H capped     {result['hours_per_module_H_capped']}h per module: {capped_days:.1f} of {active_days} commit-days count after the team-size cap "
                  f"(factor {capped_days / active_days:.3f}, computed on these same commit-days). Price with this H.")
    else:
        print("H            pass --modules N (modules shipped in this window) to get hours per module."
              f" Proxy: {len(feature_prs) or len(prs)} merged {'feature ' if feature_prs else ''}PRs.")
    if not a.alias:
        print("Check: the same person under two names? Re-run with --alias 'Name A=Name B'.")
    print("Verify H: outside 12-60h, or above 1.5x the Tier C H (50 x AI factor)? Recheck --since"
          " (AI-first date) and the module count before using it.")


if __name__ == "__main__":
    main()
