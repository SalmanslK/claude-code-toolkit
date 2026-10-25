#!/usr/bin/env python3
"""Per-module speed from git: pick-up, done, effort and spec availability. Works for backend and front-end repos.

Why this exists. "Developer-days / modules started" (measure_velocity.py --modules) mixes in shared and
foundation work, unfinished modules, rework on other modules, and days a finished spec sat unpicked. This
script measures each module on its own:

  spec-ready   date the module's spec was usable (from --spec-dates; never guessed). Optional.
  pick-up      first commit on the module. pick-up lag = pick-up - spec-ready; it is REPORTED, NEVER CHARGED.
  done         last FEATURE commit (a commit whose subject is not fix/bug/defect/revert/hotfix). Merge dates
               are not used: a late merge says nothing about build time.
  effort       hours, not calendar days. Each developer-day (author, date) is split equally across the modules
               its commits touched; a day touching no module goes to 'shared'. x hours-per-day x (1 + overhead).
  rework       fix commits and effort after the done date, kept apart from the build.
  settled      done at least --settle-days before --until, so the fix tail has mostly landed.
  team size    --team-size caps each week's commit-days at declared FTE x working days (weight <= 1), because more people
               can commit than are on the team full time. --steady-from reports class medians for modules picked up
               after the shared component library existed (a floor for later screens).
  spec-first   built before its spec was ready (pick-up < spec-ready): excluded from the spec-ready pace.

Pace to price from = median effort of settled, spec-ready modules (+ P20/P80), shared work reported once.
Standard library only. Read-only (git log).

Config (JSON): {"branch": "origin/dev", "root": "apps/web/src/features/" (optional prefix filter for paths),
 "generated": "<regex of generated files to ignore>",
 "module_rules": [{"pattern": "<regex on path>", "module": "{1}"}, ...]   first match wins; module null = shared;
   a rule may carry "keywords": [["Checkout", "OR.Checkout"], ...], "strip": "<text>", "default": "<module>"
 "classes": {"<Class>": ["<module>", ...]},                                   optional: medians per class
 "exclude": ["<module>", ...]}                                              left out of the pace (config modules)
Spec dates (CSV, header module,date): one line per module, ISO dates.

Example:
  python module_cycle.py --repo D:/repos/my-web-app --config web-modules.json --since 2026-08-27 \
      --until 2026-10-23 --spec-dates web-spec-dates.csv
"""
import argparse, collections, csv, datetime as dt, json, re, statistics, subprocess, sys

FIX = re.compile(r'\b(fix|bug|bugfix|defect|revert|hotfix)\b', re.I)


def git(repo, *a):
    return subprocess.run(['git', '-C', repo] + list(a), capture_output=True, text=True,
                          encoding='utf-8', errors='replace').stdout


def module_of(path, cfg, gen):
    if gen and re.search(gen, path):
        return 'ignore'
    for r in cfg['module_rules']:
        m = re.search(r['pattern'], path)
        if not m:
            continue
        if 'keywords' in r:
            rest = path[m.end():] if not r.get('strip') else path.split(r['strip'], 1)[-1]
            for kw, mod in r['keywords']:
                if kw.lower() in rest.lower():
                    return mod
            return r.get('default')
        mod = r.get('module')
        return mod.format('', *m.groups()) if mod and '{' in mod else mod
    return None


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return float('nan')
    k = (len(xs) - 1) * p
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', required=True); ap.add_argument('--config', required=True)
    ap.add_argument('--branch'); ap.add_argument('--since', required=True); ap.add_argument('--until', required=True)
    ap.add_argument('--team-size', help="declared team size over time, 'YYYY-MM-DD:FTE,...' (e.g. 2026-08-27:3,2026-09-28:2,2026-10-12:1); caps each week's commit-days at FTE x working days")
    ap.add_argument('--steady-from', help='ISO date: also report class medians for modules picked up on/after it (component library mature)')
    ap.add_argument('--spec-dates'); ap.add_argument('--settle-days', type=int, default=7)
    ap.add_argument('--hours-per-day', type=float, default=8); ap.add_argument('--overhead', type=float, default=0.15)
    ap.add_argument('--include-open', action='store_true', help='count unsettled modules in the class medians (their effort to date is a lower bound)')
    ap.add_argument('--exclude-author', action='append', default=[], help='leave out an author who is not on the team (repeatable; matches part of the name, case-insensitive)')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    cfg = json.load(open(a.config, encoding='utf-8'))
    branch = a.branch or cfg.get('branch') or 'HEAD'
    gen = cfg.get('generated')
    hpd = a.hours_per_day * (1 + a.overhead)
    exclude = set(cfg.get('exclude', []))
    sched = []
    if a.team_size:
        for part in a.team_size.split(','):
            d0, f0 = part.split(':'); sched.append((dt.date.fromisoformat(d0), float(f0)))
        sched.sort()
    spec = {}
    if a.spec_dates:
        for r in csv.DictReader(open(a.spec_dates, encoding='utf-8')):
            spec[r['module'].strip()] = dt.date.fromisoformat(r['date'].strip())

    out = git(a.repo, 'log', branch, '--no-merges', f'--since={a.since}', f'--until={a.until} 23:59',
              '--name-only', '--format=@@%H|%an|%ad|%s', '--date=short')
    days = collections.defaultdict(set); first = {}; last_feat = {}; last_any = {}
    ncom = collections.Counter(); nfix = collections.Counter(); commit_days = collections.defaultdict(set)
    fix_after_done = collections.Counter(); alld = set(); commits = []
    for blk in out.split('@@')[1:]:
        head, *files = blk.strip().split('\n')
        h, au, d, subj = head.split('|', 3)
        if any(x.lower() in au.lower() for x in a.exclude_author):
            continue
        d = dt.date.fromisoformat(d); mods = set()
        for f in (x for x in files if x):
            m = module_of(f, cfg, gen)
            if m == 'ignore':
                continue
            mods.add(m)
        alld.add((au, d)); days[(au, d)] |= mods
        commits.append((d, subj, mods))
        for m in mods:
            if not m or m in exclude:
                continue
            first[m] = min(first.get(m, d), d); last_any[m] = max(last_any.get(m, d), d)
            ncom[m] += 1; commit_days[m].add((au, d))
            if FIX.search(subj):
                nfix[m] += 1
            else:
                last_feat[m] = max(last_feat.get(m, d), d)
    until = dt.date.fromisoformat(a.until); since_d = dt.date.fromisoformat(a.since)

    def week_of(d):
        return d - dt.timedelta(days=d.weekday())

    wk_days = collections.Counter(); wk_auth = collections.defaultdict(set)
    for (au, d) in alld:
        wk_days[week_of(d)] += 1; wk_auth[week_of(d)].add(au)
    weight = {}
    wtable = []
    for w in sorted(wk_days):
        work = sum(1 for i in range(5) if since_d <= w + dt.timedelta(days=i) <= until)
        fte = None
        for d0, f0 in sched:
            if d0 <= w + dt.timedelta(days=4):
                fte = f0
        cap = fte * work if fte is not None else None
        wt = min(1.0, cap / wk_days[w]) if cap else 1.0
        weight[w] = wt
        wtable.append((w, len(wk_auth[w]), wk_days[w], fte, cap, wt))
    eff = collections.Counter()
    for (au, d), ms in days.items():
        ww = weight[week_of(d)]
        real = {m for m in ms if m and m not in exclude}
        if not real:
            eff['(shared)'] += hpd * ww
        else:
            for m in real:
                eff[m] += hpd * ww / len(real)
    rows = []
    for m in sorted(first, key=lambda x: first[x]):
        done = last_feat.get(m, last_any[m])
        fa = sum(1 for d, s, ms in commits if m in ms and d > done and FIX.search(s))
        sp = spec.get(m)
        lag = (first[m] - sp).days if sp else None
        settled = (until - done).days >= a.settle_days
        specfirst = sp is not None and first[m] < sp
        rows.append(dict(module=m, spec=sp, pickup=first[m], done=done, lag=lag, span=(done - first[m]).days + 1,
                         touch_days=len(commit_days[m]), commits=ncom[m], fix_pct=100 * nfix[m] / ncom[m],
                         fix_after_done=fa, effort=eff[m], settled=settled, spec_first=specfirst))
    use = [r for r in rows if r['settled'] and not r['spec_first']]
    ef = [r['effort'] for r in use]
    shared = eff['(shared)']; total = sum(weight[week_of(d)] for (au, d) in alld) * hpd
    res = dict(repo=a.repo, branch=branch, since=a.since, until=a.until, hours_per_day=hpd,
               developer_days=len(alld), counted_developer_days=total / hpd, total_hours=total, shared_hours=shared, shared_share=shared / total if total else 0,
               modules=len(rows), used=len(use),
               median=statistics.median(ef) if ef else None, mean=statistics.mean(ef) if ef else None,
               p20=pct(ef, .2) if ef else None, p80=pct(ef, .8) if ef else None,
               all_in_median=(statistics.median(ef) + shared / len(use)) if ef else None, rows=rows)
    cls = cfg.get('classes') or {}
    cmap = {m: c for c, ms in cls.items() for m in ms} if isinstance(cls, dict) else {}
    byc = collections.defaultdict(list)
    for r in rows:
        r['cls'] = cmap.get(r['module'], '-')
        if not r['spec_first'] and (r['settled'] or a.include_open):
            byc[r['cls']].append(r['effort'])
    steady = a.steady_from and dt.date.fromisoformat(a.steady_from)
    bys = collections.defaultdict(list)
    if steady:
        for r in rows:
            if r['pickup'] >= steady and not r['spec_first']:
                bys[r['cls']].append(r['effort'])
    res['steady'] = {c: dict(n=len(v), median=statistics.median(v)) for c, v in bys.items()}
    res['by_class'] = {c: dict(n=len(v), median=statistics.median(v), p20=pct(v, .2), p80=pct(v, .8)) for c, v in byc.items()}
    if a.json:
        print(json.dumps(res, default=str, indent=1)); return
    print(f"{a.repo} {branch} {a.since}..{a.until}: {len(alld)} commit-days, {total/hpd:.0f} counted after the team-size cap = {total:.0f}h at {hpd:.1f}h/day; shared {shared:.0f}h ({100*shared/total:.0f}%)")
    print('week        authors commit-days  declared FTE  capacity  weight')
    for w, na, nd, fte, cap, wt in wtable:
        print(f"{w}  {na:>6} {nd:>11}  {('-' if fte is None else fte):>12}  {('-' if cap is None else f'{cap:.0f}'):>8}  {wt:>6.2f}")
    print(f"{'module':26}{'spec':>11}{'pickup':>11}{'lag d':>6}{'done':>11}{'span d':>7}{'touch d':>8}{'fix%':>6}{'fix>done':>9}{'effort h':>9}  flags")
    for r in rows:
        fl = ('settled' if r['settled'] else 'OPEN') + (' SPEC-FIRST' if r['spec_first'] else '') + ('' if r['spec'] else ' no-spec-date')
        print(f"{r['module']:26}{str(r['spec'] or '-'):>11}{str(r['pickup']):>11}{('-' if r['lag'] is None else r['lag']):>6}{str(r['done']):>11}{r['span']:>7}{r['touch_days']:>8}{r['fix_pct']:>6.0f}{r['fix_after_done']:>9}{r['effort']:>9.1f}  {fl}")
    print(f"\nPace from {len(use)} settled spec-ready modules (of {len(rows)}): median {res['median']:.1f}h, mean {res['mean']:.1f}h, P20 {res['p20']:.1f}h, P80 {res['p80']:.1f}h")
    if byc:
        print('By class' + (' (open modules included, effort to date)' if a.include_open else ' (settled only)') + ':')
        for c, d in sorted(res['by_class'].items()):
            print(f"  {c:28} n={d['n']:2} median {d['median']:.1f}h  P20 {d['p20']:.1f}h  P80 {d['p80']:.1f}h")
    if steady:
        print(f'Steady state (modules picked up on/after {steady}, library mature):')
        for c, d in sorted(res['steady'].items()):
            print(f"  {c:28} n={d['n']:2} median {d['median']:.1f}h")
    print(f"Shared work: {shared:.0f}h ({100*res['shared_share']:.0f}% of all hours); median module + equal share of shared = {res['all_in_median']:.1f}h")


if __name__ == '__main__':
    main()
