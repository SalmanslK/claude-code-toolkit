#!/usr/bin/env python3
"""Build a reference-module catalogue from git and code: hours, size and K per class.

For every module slice it measures:
  - actual hours, rework included: each author-day is split across the modules whose files it
    touched (by files touched, generated files excluded), x hours-per-day x (1 + overhead);
  - size S = endpoints + entities + 0.5 x rules + 0.5 x links to other modules, counted from code.

From the finished modules it derives what the estimating skill prices with:
  - K per class (hours per size point), platform share included;
  - alpha, the share of hours no module owns (platform work), already inside K;
  - sigma, the spread of actual / predicted, leave-one-out;
  - the single-module P20 / P80 multipliers (min and max) and the pooled 80% bid factor.

Standard library only. Read-only: runs `git log` and reads files.

Examples:
  python module_catalogue.py --repo . --since 2026-08-27
  python module_catalogue.py --repo . --since 2026-08-27 --config my-modules.json --json

The default config fits a .NET slice layout: <Layer>/Features/<Module>/..., API in Endpoints/<Module>/,
minimal-API routes, AggregateRoot/Entity classes, Error.<Kind>(...) rules in *Errors.cs and
`using ...Features.<Module>` links. For another stack, write a config (see --help-config).
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import re
import statistics
import subprocess
import sys

DEFAULT_CONFIG = {
    "branch": None,
    "paths": ["src", "tests"],
    "generated": r"(/Migrations/|\.Designer\.cs$|ModelSnapshot\.cs$)",
    "module_rules": [
        {"pattern": r"/(?:Features|Endpoints)/([^/.]+)/", "module": "{1}"}
    ],
    "source_root": "src",
    "source_ext": [".cs"],
    "skip_dirs": ["bin", "obj", "Migrations", "node_modules"],
    "drivers": {
        "endpoints": {"pattern": r"\.Map(?:Get|Post|Put|Patch|Delete)\("},
        "entities": {"pattern": r"class \w+\s*:\s*(?:AggregateRoot|Entity)\b"},
        "rules": {"pattern": r"Error\.(?:Validation|Conflict|NotFound|Failure|Forbidden|Unauthorized)\(",
                  "file": r"Errors\.cs$"},
        "links": {"pattern": r"using [\w.]+\.Features\.([\w.]+);", "as_path": "/Features/{0}/x"}
    },
    "classes": {},
    "exclude": []
}
CONFIG_HELP = """Config (JSON). Every key is optional; missing keys take the defaults.
  paths          folders whose commits count (default ["src","tests"])
  generated      regex of generated files left out of the hours split
  module_rules   ordered list, first match wins, on the '/'-separated path:
                   {"pattern": regex, "module": "Name or {1}"}         capture-group template
                   {"pattern": regex, "module": null}                  platform/shared work
                   {"pattern": regex, "keywords": [[kw, Name], ...],
                    "strip": "text removed before keyword search", "default": Name}
                 "aliases": {"Auth": "Users"} at top level merges module names afterwards.
  source_root, source_ext, skip_dirs   where size is counted
  drivers        endpoints / entities / rules: {"pattern": regex, "file": regex limiting files}
                 links: {"pattern": regex capturing a reference, "as_path": "/Features/{0}/x"}
                 (dots in the capture become '/', then the path is mapped with module_rules)
  classes        {"Module": "crud" | "workflow" | "readonly" | ...}  needed for K per class
  exclude        modules left out of K (infrastructure slices, unfinished work)
  first_of_kind  modules that set a new pattern (usually the first one built); left out of K
                 and reported as the first-of-kind factor F"""
SHARED = "(platform/shared)"


def load_config(path):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if path:
        user = json.load(open(path, encoding="utf-8"))
        for k, v in user.items():
            if k == "drivers":
                cfg["drivers"].update(v)
            else:
                cfg[k] = v
    cfg["_rules"] = [dict(r, rx=re.compile(r["pattern"])) for r in cfg["module_rules"]]
    cfg["_aliases"] = cfg.get("aliases", {})
    return cfg


def module_of(cfg, path):
    path = "/" + path.replace("\\", "/").lstrip("/")
    for rule in cfg["_rules"]:
        m = rule["rx"].search(path)
        if not m:
            continue
        if "keywords" in rule:
            tail = path[m.start():]
            if rule.get("strip"):
                tail = tail.replace(rule["strip"], "")
            name = next((n for kw, n in rule["keywords"] if kw in tail), rule.get("default"))
        else:
            tmpl = rule.get("module")
            if tmpl is None:
                return None
            name = re.sub(r"\{(\d+)\}", lambda g: m.group(int(g.group(1))), tmpl)
        return cfg["_aliases"].get(name, name)
    return None


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def detect_branch(repo):
    for ref in ("origin/dev", "origin/develop", "origin/main", "origin/master", "dev", "main", "master"):
        if subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", ref],
                          capture_output=True).returncode == 0:
            return ref
    return "HEAD"


def measure_hours(cfg, a, branch):
    window = [f"--since={a.since}"] + ([f"--until={a.until} 23:59"] if a.until else [])
    log = git(a.repo, "log", branch, "--no-merges", *window, "--format=@@%an|%ad", "--date=short",
              "--numstat", "--", *cfg["paths"])
    generated = re.compile(cfg["generated"])
    day_files = collections.defaultdict(collections.Counter)
    first, last = {}, {}
    key = None
    for line in log.splitlines():
        if line.startswith("@@"):
            author, date = line[2:].split("|")
            if any(x.lower() in author.lower() for x in a.exclude_author):
                key = None
            else:
                key = (author, date)
            continue
        parts = line.split("\t")
        if key is None or len(parts) != 3 or generated.search(parts[2]):
            continue
        path = re.sub(r"\{[^{}]*=> ([^{}]*)\}", r"\1", parts[2]).replace("//", "/").split(" => ")[-1]
        mod = module_of(cfg, path) or SHARED
        day_files[key][mod] += 1
        if mod != SHARED:
            first[mod] = min(first.get(mod, key[1]), key[1])
            last[mod] = max(last.get(mod, key[1]), key[1])
    weight = week_weights(a, day_files)
    hours = collections.Counter()
    for (au, d), counts in day_files.items():
        total = sum(counts.values())
        wt = weight(d)
        for mod, n in counts.items():
            hours[mod] += n / total * a.hours_per_day * (1 + a.overhead) * wt
    return hours, first, last, len(day_files)


def week_weights(a, day_files):
    """--team-size 'YYYY-MM-DD:FTE,...': cap each week's commit-days at FTE x working days (weight <= 1).
    Same rule as module_cycle.py, so K, sigma and alpha are fitted on the same capped hours as the per-module sets."""
    if not getattr(a, "team_size", None):
        return lambda d: 1.0
    sched = sorted((datetime.date.fromisoformat(x.split(":")[0]), float(x.split(":")[1])) for x in a.team_size.split(","))
    wk = collections.Counter()
    for (au, d) in day_files:
        dd = datetime.date.fromisoformat(d)
        wk[dd - datetime.timedelta(days=dd.weekday())] += 1
    until = datetime.date.fromisoformat(a.until) if a.until else None
    since = datetime.date.fromisoformat(a.since)
    wts = {}
    for w, n in wk.items():
        days = [w + datetime.timedelta(days=i) for i in range(5)]
        work = sum(1 for x in days if x >= since and (until is None or x <= until))
        fte = None
        for d0, f0 in sched:
            if d0 <= w + datetime.timedelta(days=4):
                fte = f0
        wts[w] = min(1.0, fte * work / n) if fte else 1.0
    def weight(d):
        dd = datetime.date.fromisoformat(d)
        return wts[dd - datetime.timedelta(days=dd.weekday())]
    return weight


def measure_size(cfg, repo):
    drv = {k: dict(v, rx=re.compile(v["pattern"]), frx=re.compile(v["file"]) if v.get("file") else None)
           for k, v in cfg["drivers"].items()}
    counts = collections.defaultdict(collections.Counter)
    links = collections.defaultdict(set)
    root = os.path.join(repo, cfg["source_root"])
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in cfg["skip_dirs"]]
        for name in files:
            if not any(name.endswith(e) for e in cfg["source_ext"]):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, repo).replace("\\", "/")
            mod = module_of(cfg, rel)
            if mod is None:
                continue
            text = open(full, encoding="utf-8", errors="replace").read()
            for k in ("endpoints", "entities", "rules"):
                d = drv.get(k)
                if d and (d["frx"] is None or d["frx"].search(name)):
                    counts[mod][k] += len(d["rx"].findall(text))
            d = drv.get("links")
            if d:
                for ref in d["rx"].findall(text):
                    other = module_of(cfg, d["as_path"].format(ref.replace(".", "/")))
                    if other and other != mod:
                        links[mod].add(other)
    for mod in counts:
        counts[mod]["links"] = len(links[mod])
    return counts


def size_of(c):
    return c["endpoints"] + c["entities"] + 0.5 * c["rules"] + 0.5 * c["links"]


def quantile(sorted_vals, p):
    if not sorted_vals:
        return None
    pos = p * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".")
    p.add_argument("--since", help="YYYY-MM-DD, no earlier than the AI-first date (required)")
    p.add_argument("--until", help="YYYY-MM-DD")
    p.add_argument("--config", help="JSON config; see --help-config")
    p.add_argument("--hours-per-day", type=float, default=8.0)
    p.add_argument("--overhead", type=float, default=0.15)
    p.add_argument("--settle-days", type=int, default=14,
                   help="leave out modules started fewer than this many days before the window end"
                        " (they have not had their rework rounds yet)")
    p.add_argument("--exclude-author", action="append", default=[])
    p.add_argument("--team-size", help="declared team size over time, 'YYYY-MM-DD:FTE,...'; caps each week's commit-days at FTE x working days, as in module_cycle.py")
    p.add_argument("--help-config", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if a.help_config:
        print(CONFIG_HELP)
        return
    if not a.since:
        p.error("--since is required (the date the team went AI-first, or the window start)")
    cfg = load_config(a.config)
    repo = os.path.abspath(a.repo)
    branch = cfg.get("branch") or detect_branch(repo)
    hours, first, last, author_days = measure_hours(cfg, a, branch)
    sizes = measure_size(cfg, repo)
    if not hours:
        sys.exit("No commits in the window.")

    end = a.until or max(last.values())
    settle_cut = (datetime.date.fromisoformat(end) - datetime.timedelta(days=a.settle_days)).isoformat()
    total = sum(hours.values())
    shared = hours.get(SHARED, 0.0)
    alpha = shared / (total - shared) if total > shared else 0.0
    alloc = 1 + alpha

    rows, sample = [], []
    for mod in sorted(set(hours) | set(sizes)):
        if mod == SHARED:
            continue
        c = sizes.get(mod, collections.Counter())
        row = {"module": mod, "class": cfg["classes"].get(mod), "hours_direct": round(hours.get(mod, 0), 1),
               "hours": round(hours.get(mod, 0) * alloc, 1), "first": first.get(mod), "last": last.get(mod),
               "endpoints": c["endpoints"], "entities": c["entities"], "rules": c["rules"], "links": c["links"],
               "size": size_of(c)}
        reason = None
        if mod in cfg["exclude"]:
            reason = "excluded by config"
        elif mod in cfg.get("first_of_kind", []):
            reason = "first of its kind: gives F, not K"
        elif row["size"] == 0:
            reason = "no size drivers"
        elif row["first"] and row["first"] > settle_cut:
            reason = f"started after {settle_cut}"
        row["used"] = reason is None
        row["why_not"] = reason
        rows.append(row)
        if reason is None:
            sample.append(row)

    by_class = collections.defaultdict(list)
    for r in sample:
        by_class[r["class"] or "unclassified"].append(r)
    k_class = {c: sum(r["hours"] for r in rs) / sum(r["size"] for r in rs) for c, rs in by_class.items()}
    k_pooled = sum(r["hours"] for r in sample) / sum(r["size"] for r in sample) if sample else None

    ratios = []
    for r in sample:
        peers = [o for o in by_class[r["class"] or "unclassified"] if o is not r]
        pool = peers if len(peers) >= 2 else [o for o in sample if o is not r]
        k = sum(o["hours"] for o in pool) / sum(o["size"] for o in pool)
        r["predicted"] = round(k * r["size"], 1)
        r["ratio"] = round(r["hours"] / (k * r["size"]), 2)
        ratios.append(r["hours"] / (k * r["size"]))
    ratios.sort()
    first_of_kind = {}
    for r in rows:
        if r["module"] in cfg.get("first_of_kind", []) and r["size"]:
            k = k_class.get(r["class"] or "unclassified", k_pooled)
            r["ratio"] = round(r["hours"] / (k * r["size"]), 2)
            first_of_kind[r["module"]] = r["ratio"]
    sigma = statistics.pstdev(ratios) if len(ratios) > 1 else None
    mean = statistics.mean(ratios) if ratios else None
    ape = sorted(abs(x - 1) for x in ratios)
    result = {
        "branch": branch, "since": a.since, "until": end, "author_days": author_days,
        "total_hours": round(total), "shared_hours": round(shared), "alpha": round(alpha, 2),
        "k_by_class": {c: round(v, 2) for c, v in k_class.items()},
        "k_pooled": round(k_pooled, 2) if k_pooled else None,
        "modules_used": len(sample), "loo_median_error": round(quantile(ape, .5), 2) if ape else None,
        "ratio_mean": round(mean, 2) if mean else None, "sigma": round(sigma, 2) if sigma else None,
        "min_multiplier_p20": round(quantile(ratios, .2), 2) if ratios else None,
        "max_multiplier_p80": round(quantile(ratios, .8), 2) if ratios else None,
        "bid80_factor": {n: round(1 + 0.84 * sigma / n ** .5, 2) for n in (1, 4, 8, 16)} if sigma else None,
        "first_of_kind_F": first_of_kind,
        "modules": rows,
    }
    if a.json:
        print(json.dumps(result, indent=1))
        return

    print(f"Branch {branch}  window {a.since} -> {end}  {author_days} developer-days  "
          f"~{total:.0f}h ({a.hours_per_day:g}h x {1 + a.overhead:g} per day with a commit)")
    print(f"Platform/shared {shared:.0f}h -> alpha {alpha:.2f} (spread over every module's hours, so K includes it)")
    print(f"\n{'module':24}{'class':10}{'hours':>7}{'ep':>4}{'ent':>4}{'rul':>5}{'lnk':>4}{'size':>6}"
          f"{'h/pt':>6}{'act/pred':>9}  first       note")
    for r in sorted(rows, key=lambda r: (not r["used"], -r["hours"])):
        hp = f"{r['hours'] / r['size']:.2f}" if r["size"] else "-"
        print(f"{r['module'][:23]:24}{(r['class'] or '-'):10}{r['hours']:7.0f}{r['endpoints']:4}{r['entities']:4}"
              f"{r['rules']:5}{r['links']:4}{r['size']:6.1f}{hp:>6}{str(r.get('ratio', '')):>9}  "
              f"{r['first'] or '-':11} {r['why_not'] or ''}")
    if not sample:
        print("\nNo finished modules with size: cannot derive K. Price from the ratio table.")
        return
    print(f"\nK (hours per size point): " + ", ".join(f"{c} {v:.2f} (n={len(by_class[c])})" for c, v in k_class.items())
          + f"; pooled {k_pooled:.2f}")
    if not cfg["classes"]:
        print("  No classes in the config: every module shares one K. Add 'classes' to price CRUD and workflow apart.")
    print(f"Leave-one-out: median error {result['loo_median_error']:.0%}, actual/predicted mean {mean:.2f}, sigma {sigma:.2f}")
    print(f"Single module: min = {result['min_multiplier_p20']:.2f} x E (P20), max = {result['max_multiplier_p80']:.2f} x E (P80)")
    print("80% bid factor 1 + 0.84 x sigma / sqrt(n): " +
          ", ".join(f"n={n} {v:.2f}" for n, v in result["bid80_factor"].items()))
    if first_of_kind:
        print("First-of-kind factor F (actual / K x size): " +
              ", ".join(f"{m} {v:.2f}" for m, v in first_of_kind.items()))
    else:
        print("First-of-kind: none named in the config. The module that set the team's patterns usually costs"
              " about 2x; name it under 'first_of_kind' so it does not inflate K.")
    small = [c for c, rs in by_class.items() if len(rs) < 3]
    if small:
        print(f"Check: fewer than 3 finished modules in {', '.join(small)}; do not price that class from K.")
    print("Check: size here is counted from code. Size for new work comes from the spec; apply the spec-to-code"
          " factor before multiplying by K (SKILL.md section 3).")


if __name__ == "__main__":
    main()
