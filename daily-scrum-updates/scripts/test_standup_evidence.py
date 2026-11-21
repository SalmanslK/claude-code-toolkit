"""Tests for standup_evidence.py - one or more per safeguard S1-S23 listed in its docstring.

Run:  python -m unittest discover -s ~/.claude/skills/daily-scrum-updates/scripts -p "test_*.py" -v
Builds throwaway git repositories and a fake Claude Code projects folder under the system temp folder.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import standup_evidence as se  # noqa: E402

# Keep the person's own git settings (hooks, signing, aliases) out of the fixture.
_EMPTY = Path(tempfile.mkdtemp(prefix="se-gitcfg-")) / "empty.gitconfig"
_EMPTY.write_text("", encoding="utf-8")
os.environ["GIT_CONFIG_GLOBAL"] = str(_EMPTY)
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
os.environ.pop("CLAUDE_CONFIG_DIR", None)

LEAD = ("Lead Person", "lead@x.test")
LEAD_ALIAS = ("Lead P", "lead.bb@x.test")
ALICE = ("Alice", "alice@x.test")
ALICE_BB = ("Alice*", "alice.bb@x.test")
BOB = ("Bob", "bob@x.test")
CAROL = ("Carol", "carol@x.test")
AUTHORS = {"lead@x.test": "Lead Person", "lead.bb@x.test": "Lead Person", "alice@x.test": "Alice",
           "alice.bb@x.test": "Alice", "bob@x.test": "Bob", "dana@x.test": "Dana"}
NOW = "2026-11-16T09:00:00Z"   # Monday 14:00 PKT


def run_git(repo: Path, *args: str, date: str | None = None, author=LEAD, committer=None) -> str:
    committer = committer or author
    env = dict(os.environ)
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    env.update(GIT_AUTHOR_NAME=author[0], GIT_AUTHOR_EMAIL=author[1],
               GIT_COMMITTER_NAME=committer[0], GIT_COMMITTER_EMAIL=committer[1])
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError(f"git {args}: {p.stderr}")
    return p.stdout


def commit(repo: Path, who, date: str, msg: str, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        run_git(repo, "add", "-f", name)
    run_git(repo, "commit", "-q", "-m", msg, date=date, author=who)


def merge(repo: Path, branch: str, msg: str, date: str, author, committer) -> None:
    run_git(repo, "merge", "-q", "--no-ff", branch, "-m", msg, date=date, author=author, committer=committer)


def build_fixture(root: Path) -> Path:
    repo = root / "Proj-Repo"
    repo.mkdir()
    run_git(repo, "init", "-q", "-b", "dev")
    for k, v in (("user.name", LEAD[0]), ("user.email", LEAD[1]), ("commit.gpgsign", "false"),
                 ("core.autocrlf", "false")):
        run_git(repo, "config", k, v)
    commit(repo, LEAD, "2026-11-09T10:00:00+05:00", "Initial", {"README.md": "x"})
    run_git(repo, "checkout", "-q", "-b", "feature/a")
    commit(repo, ALICE, "2026-11-10T11:00:00+05:00", "Add packing list", {"src/packing.cs": "1", "bin/out.dll": "b"})
    commit(repo, ALICE, "2026-11-10T23:50:00+05:00", "Late commit", {"src/packing.cs": "2"})
    commit(repo, ALICE, "2026-11-11T00:11:00+05:00", "After midnight", {"src/packing.cs": "3"})
    run_git(repo, "checkout", "-q", "dev")
    commit(repo, LEAD, "2026-11-10T15:00:00+05:00", "Direct tweak", {"README.md": "y"})
    run_git(repo, "checkout", "-q", "feature/a")
    commit(repo, LEAD, "2026-11-11T09:00:00+05:00", "Fix review", {"src/packing.cs": "4"})
    merge(repo, "dev", "Merge branch 'dev' into feature/a", "2026-11-11T09:30:00+05:00", LEAD, LEAD)
    run_git(repo, "checkout", "-q", "dev")
    merge(repo, "feature/a", "Merged in feature/a (pull request #12)\n\nPacking list for the front end",
          "2026-11-12T10:00:00+05:00", ALICE_BB, LEAD)
    run_git(repo, "checkout", "-q", "-b", "feature/b")
    commit(repo, BOB, "2026-11-12T11:00:00+05:00", "Bob one", {"src/b.cs": "1"})
    commit(repo, BOB, "2026-11-12T11:30:00+05:00", "Bob two", {"src/b.cs": "2"})
    commit(repo, LEAD, "2026-11-12T11:45:00+05:00", "Lead nit", {"src/b.cs": "3"})
    run_git(repo, "checkout", "-q", "dev")
    merge(repo, "feature/b", "Merged in feature/b (pull request #13)", "2026-11-12T15:00:00+05:00", LEAD, LEAD)
    run_git(repo, "checkout", "-q", "-b", "feature/c")
    commit(repo, ALICE, "2026-11-13T09:00:00+05:00", "Alice c", {"src/c.cs": "1"})
    commit(repo, BOB, "2026-11-13T09:10:00+05:00", "Bob c", {"src/c.cs": "2"})
    run_git(repo, "checkout", "-q", "dev")
    merge(repo, "feature/c", "Merged in feature/c (pull request #14)", "2026-11-13T12:00:00+05:00", BOB, ALICE)
    run_git(repo, "checkout", "-q", "-b", "feature/gh")
    commit(repo, ALICE, "2026-11-13T13:00:00+05:00", "GH work", {"src/gh.cs": "1"})
    run_git(repo, "checkout", "-q", "dev")
    merge(repo, "feature/gh", "Merge pull request #15 from org/feature/gh", "2026-11-13T14:00:00+05:00",
          ALICE, ALICE)
    run_git(repo, "checkout", "-q", "-b", "feature/open")
    commit(repo, BOB, "2026-11-13T10:00:00+05:00", "Open work", {"src/open.cs": "1"})
    commit(repo, CAROL, "2026-11-13T10:30:00+05:00", "Carol work", {"src/open.cs": "2"})
    commit(repo, BOB, "2026-11-14T10:00:00+05:00", "Weekend fix", {"src/open.cs": "3"})
    run_git(repo, "checkout", "-q", "dev")
    commit(repo, LEAD_ALIAS, "2026-11-13T16:00:00+05:00", "Alias commit", {"README.md": "z"})
    (repo / "README.md").write_text("stash me", encoding="utf-8")
    run_git(repo, "stash", "push", "-q", "-m", "wip", date="2026-11-12T12:00:00+05:00", author=LEAD)
    return repo


def jl(**o) -> str:
    return json.dumps(o) + "\n"


def write_transcripts(projects: Path, repo: Path) -> Path:
    d = projects / se.slug(repo)
    d.mkdir(parents=True)
    long_prompt = "Please review " + "x" * 600
    lines = [
        jl(type="ai-title", aiTitle="Review the packing PR", sessionId="s1"),
        jl(type="user", timestamp="2026-11-11T20:00:00.000Z", gitBranch="dev",
           message={"role": "user", "content": "Late night prompt counts for the 12th"}),
        jl(type="user", timestamp="2026-11-12T05:00:00.000Z", gitBranch="dev", uuid="u-review",
           message={"role": "user", "content": "Review PR 12 please<system-reminder>hidden reminder</system-reminder>"}),
        jl(type="user", timestamp="2026-11-12T05:01:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content": "TOOL OUTPUT SHOULD NOT SHOW"}]}),
        jl(type="user", timestamp="2026-11-12T05:02:00.000Z", isSidechain=True,
           message={"role": "user", "content": "SIDECHAIN SHOULD NOT SHOW"}),
        jl(type="user", timestamp="2026-11-12T05:03:00.000Z", isMeta=True,
           message={"role": "user", "content": "META SHOULD NOT SHOW"}),
        jl(type="user", timestamp="2026-11-12T05:04:00.000Z", isCompactSummary=True,
           message={"role": "user", "content": "COMPACT SHOULD NOT SHOW"}),
        jl(type="user", timestamp="2026-11-12T05:05:00.000Z",
           message={"role": "user", "content": "<command-name>/commit</command-name><command-args>now</command-args>"}),
        jl(type="user", timestamp="2026-11-12T05:06:00.000Z", message={"role": "user", "content": long_prompt}),
        jl(type="assistant", timestamp="2026-11-12T06:00:00.000Z",
           message={"role": "assistant", "content": [{"type": "text", "text": "Done: PR 12 reviewed and merged."}]}),
    ]
    (d / "sess0001-aaaa.jsonl").write_text("".join(lines), encoding="utf-8")
    resumed = [lines[2],                                                       # copied from the parent session
               jl(type="assistant", timestamp="2026-11-12T07:00:00.000Z", isApiErrorMessage=True, uuid="u-err",
                  message={"role": "assistant", "content": [{"type": "text", "text": "API ERROR SHOULD NOT SHOW"}]}),
               jl(type="user", timestamp="2026-11-12T07:01:00.000Z", uuid="u-new",
                  message={"role": "user", "content": "Resumed session prompt"})]
    (d / "sess0002-cccc.jsonl").write_text("".join(resumed), encoding="utf-8")
    report_new = ("Deployment complete — smoke passed.\n  Environment:  DEV\n  Branch:       dev\n"
                  "  Commit:       abcdef123456\n  Changed:      3 commits\n  Reached at:   http://10.9.8.7:8080\n"
                  "Host:         deployer@10.9.8.7:/srv/app")
    deploy_lines = [
        jl(type="user", timestamp="2026-11-12T10:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content": report_new}]}),
        jl(type="user", timestamp="2026-11-13T10:00:00.000Z",           # same env+commit later: dedupe keeps earliest
           message={"role": "user", "content": [{"type": "tool_result", "content": report_new}]}),
        jl(type="assistant", timestamp="2026-09-03T09:00:00.000Z",
           message={"role": "assistant", "content": [{"type": "text", "text":
                    "```\nDeployment complete.\n  Environment:  QA\n  Branch:       dev\n  Commit:       1234567\n```"}]}),
        jl(type="user", timestamp="2026-11-13T11:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "Deployed — smoke SKIPPED at the user's request. Only the health checks verified it.\n"
                    "WARNING: something\n  Environment:  QA\n  Branch:       dev\n  Commit:       fedcba987654"}]}),
        jl(type="user", timestamp="2026-11-13T12:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "Reverted to 0123456789ab after the smoke failed. Deployed — post-deploy smoke FAILED. x\n"
                    "  Environment:  DEV\n  Branch:       feature/x\n  Commit:       0123456789ab"}]}),
        jl(type="user", timestamp="2026-11-13T13:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "NOT deployed — the run stopped before `factory deploy up`.\n  Environment:  DEV\n"
                    "  Branch:       dev\n  Commit:       999999999999"}]}),
        jl(type="user", timestamp="2026-11-13T14:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "Deploy FAILED — `up` failed.\n  Environment:  DEV\n  Branch:       dev\n  Commit:       888888888888"}]}),
        jl(type="user", timestamp="2026-11-13T15:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "Deployment complete — smoke passed.\n  Environment:  {env}\n  Branch:       {branch}\n"
                    "  Commit:       {sha}"}]}),
        jl(type="user", timestamp="2026-11-13T16:00:00.000Z",
           message={"role": "user", "content": [{"type": "tool_result", "content":
                    "   12\tDeployment complete.\n   13\t  Environment:  DEV\n   14\t  Branch:  dev\n   15\t  Commit:  7777777"}]}),
        jl(type="assistant", timestamp="2026-11-14T11:00:00.000Z",                # relayed in the assistant's words
           message={"role": "assistant", "content": [{"type": "text", "text":
                    "Deployed to QA — smoke SKIPPED. The pre-deploy gate was also SKIPPED.\n\n```\n"
                    "  Environment:  QA\n  Commit:       4444444bbbbb (was 1111111)\n```"}]}),   # no Branch line
        jl(type="assistant", timestamp="2026-11-14T12:00:00.000Z",                # fields with no verdict above
           message={"role": "assistant", "content": [{"type": "text", "text":
                    "Here is the deploy target I will use:\n  Environment:  DEV\n  Branch:       dev\n"
                    "  Commit:       3333333"}]}),
    ]
    raw = json.dumps({"type": "user", "timestamp": "2026-11-14T10:00:00.000Z", "message": {"role": "user", "content": [
        {"type": "tool_result", "content": "Deployed — smoke passed IN PART. 40 ran; 3 authenticated checks skipped.\n"
                                           "  Environment:  QA\n  Branch:  qa\n  Commit:  5555555aaaaa"}]}},
                     ensure_ascii=False) + "\n"
    (d / "deploy01-bbbb.jsonl").write_text("".join(deploy_lines) + raw, encoding="utf-8")
    return d


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="se-test-"))      # left unresolved: may be an 8.3 short path
        cls.repo = build_fixture(cls.tmp)
        cls.projects = cls.tmp / "projects"
        write_transcripts(cls.projects, cls.repo)
        cls.logs = cls.tmp / "logs"
        cls.logs.mkdir()
        cls.config = cls.tmp / "config.json"
        cls.config.write_text(json.dumps({"directory": str(cls.logs), "authors": AUTHORS,
                                          "deployment": {"integrationBranch": "dev", "mergeDeploysTo": "DEV"}}),
                              encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        for f in self.logs.iterdir():
            f.unlink()

    def run_cli(self, *argv: str, config: Path | None = None, now: str = NOW, extra=()) -> tuple[int, str]:
        out = io.StringIO()
        code = se.main(["--repo", str(self.repo), "--config", str(config or self.config), "--now", now,
                        "--projects-dir", str(self.projects), *extra, *argv], out=out)
        return code, out.getvalue()

    def day_block(self, text: str, day: str) -> str:
        m = re.search(rf"^=== {day}.*?(?=^=== |\Z)", text, re.S | re.M)
        self.assertIsNotNone(m, f"no block for {day} in:\n{text}")
        return m.group(0)

    def write_log(self, log: str, body: str) -> Path:
        path = self.logs / se.LOG_FILES[log].format(p="Proj-Repo")
        path.write_text(body, encoding="utf-8")
        return path


class TimeAndDates(Fixture):
    def test_S1_today_is_utc_plus_offset_not_machine_zone(self):
        clock = se.Clock(se.parse_now("2026-11-15T20:30:00Z"), se.parse_offset("+05:00"))
        self.assertEqual(clock.today, dt.date(2026, 11, 16))        # 01:30 PKT on the 16th
        clock = se.Clock(se.parse_now("2026-11-15T18:59:00Z"), se.parse_offset("+05:00"))
        self.assertEqual(clock.today, dt.date(2026, 11, 15))
        _, out = self.run_cli("status", "--log", "scrum", now="2026-11-15T20:30:00Z")
        self.assertIn("NOW 2026-11-16 01:30 (UTC+05:00; Mon)", out)

    def test_S2_commits_bucket_by_author_date_in_the_offset(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-10")
        block = self.day_block(out, "2026-11-10")
        self.assertIn("Late commit", block)                 # 23:50 PKT stays on the 10th
        self.assertNotIn("After midnight", block)           # 00:11 belongs to the 11th
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-11")
        self.assertIn("After midnight", self.day_block(out, "2026-11-11"))

    def test_S15_date_words(self):
        today = dt.date(2026, 11, 16)
        notes: list[str] = []
        self.assertEqual(se.parse_one_date("2026-09-08", today, notes), dt.date(2026, 9, 8))
        self.assertEqual(se.parse_one_date("09-08-2026", today, notes), dt.date(2026, 9, 8))
        self.assertTrue(any("September 8, 2026" in n for n in notes), notes)       # ambiguous: said back
        self.assertEqual(se.parse_one_date("Sep 8", today, []), dt.date(2026, 9, 8))
        self.assertEqual(se.parse_one_date("September 8", today, []), dt.date(2026, 9, 8))
        future: list[str] = []
        self.assertEqual(se.parse_one_date("Dec 20", today, future), dt.date(2025, 12, 20))   # future -> last year
        self.assertTrue(future)
        self.assertEqual(se.parse_one_date("yesterday", today, []), dt.date(2026, 11, 15))
        clock = se.Clock(se.parse_now(NOW), se.parse_offset("+05:00"))
        cfg = se.load_config(self.config)
        week = se.plan_dates("this week", "scrum", {}, clock, cfg)
        self.assertEqual([d.date for d in week.days], [dt.date(2026, 11, 16)])
        last = se.plan_dates("last week", "scrum", {}, clock, cfg)
        self.assertEqual(last.days[0].date, dt.date(2026, 11, 9))
        self.assertEqual(last.days[-1].date, dt.date(2026, 11, 15))
        month = se.plan_dates("this month", "scrum", {}, clock, cfg)
        self.assertEqual((month.days[0].date, month.days[-1].date), (dt.date(2026, 11, 1), today))
        entries = {dt.date(2026, 11, 12): "final"}
        bf = se.plan_dates("backfill 2", "scrum", entries, clock, cfg)
        self.assertEqual([d.date for d in bf.days], [dt.date(2026, 11, 10), dt.date(2026, 11, 11)])
        self.assertIsNotNone(bf.announce)
        rng = se.plan_dates("backfill 2026-11-02..2026-11-04", "scrum", {}, clock, cfg)
        self.assertEqual(len(rng.days), 3)
        bare = se.plan_dates("backfill", "scrum", entries, clock, cfg, earliest_evidence=dt.date(2026, 11, 9))
        self.assertEqual(bare.announce, "2026-11-09..2026-11-11 (3 calendar days)")
        _, out = self.run_cli("dates", "--log", "team", "backfill")
        self.assertIn("ANNOUNCE before writing anything", out)
        with self.assertRaises(ValueError):
            se.plan_dates("next fortnight", "scrum", {}, clock, cfg)

    def test_S14_first_run_window_and_explicit_date_on_new_file(self):
        clock = se.Clock(se.parse_now(NOW), se.parse_offset("+05:00"))
        cfg = se.load_config(self.config)
        first = se.plan_dates("", "scrum", {}, clock, cfg)
        self.assertEqual([d.date.day for d in first.days], [10, 11, 12, 13, 16])
        one = se.plan_dates("2026-11-11", "scrum", {}, clock, cfg)
        self.assertEqual([d.date for d in one.days], [dt.date(2026, 11, 11)])

    def test_S9_non_working_days_skipped_unless_evidence_or_explicit(self):
        _, out = self.run_cli("evidence", "--log", "team", "last", "week")
        self.assertIn("-> WRITE", self.day_block(out, "2026-11-14"))            # Saturday with a commit
        self.assertIn("SKIP - non-working day, no evidence", self.day_block(out, "2026-11-15"))
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-15")      # explicit Sunday: still runs
        self.assertIn("NO EVIDENCE", self.day_block(out, "2026-11-15"))
        cfg = json.loads(self.config.read_text())
        cfg["holidays"] = ["2026-11-11"]
        hol = self.tmp / "holiday.json"
        hol.write_text(json.dumps(cfg))
        clock = se.Clock(se.parse_now(NOW), se.parse_offset("+05:00"))
        self.assertFalse(se.is_working(dt.date(2026, 11, 11), se.load_config(hol)))

    def test_S13_future_date_gathers_nothing(self):
        _, out = self.run_cli("evidence", "--log", "scrum", "tomorrow")
        self.assertIn("FUTURE", self.day_block(out, "2026-11-17"))
        self.assertNotIn("COMMITS", out)


class Entries(Fixture):
    def test_S10_existing_entries_are_authoritative_and_week_headings_are_not_dates(self):
        self.write_log("scrum", "# Daily\n\n## Week: 2026-11-09 – 2026-11-13\n\n* x\n\n## 2026-11-12\n\n* done\n")
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-12")
        self.assertIn("EXISTS - authoritative", out)
        self.assertNotIn("COMMITS", out)
        entries = se.read_entries(self.logs / "Proj-Repo-Daily-Updates.md")
        self.assertEqual(list(entries), [dt.date(2026, 11, 12)])
        _, out = self.run_cli("dates", "--log", "scrum")
        self.assertIn("MODE default (fill missing)", out)
        self.assertIn("DATE 2026-11-13", out)
        self.assertNotIn("DATE 2026-11-12", out)

    def test_S11_provisional_section_is_replaced_and_today_is_written_provisional(self):
        self.write_log("team", "# Team\n\n## 2026-11-13\n\n_Provisional — as of 18:00 PKT_\n\n### Bob\n* x\n")
        _, out = self.run_cli("evidence", "--log", "team")
        self.assertIn("REPLACE the provisional section (day is over: drop the marker)", self.day_block(out, "2026-11-13"))
        _, out = self.run_cli("evidence", "--log", "team", "today", now="2026-11-13T12:00:00Z")
        self.assertIn("REPLACE the provisional section (still provisional: today)", self.day_block(out, "2026-11-13"))
        self.setUp()                                                    # no section yet: a fresh today
        _, out = self.run_cli("evidence", "--log", "team", "today", now="2026-11-13T12:00:00Z")
        block = self.day_block(out, "2026-11-13")
        self.assertIn("WRITE (provisional: today is not over)", block)
        self.assertIn("MARKER first line: _Provisional — as of 17:00 PKT_", block)

    def test_S12_scrum_today_only_with_evidence(self):
        self.write_log("scrum", "# Daily\n\n## 2026-11-13\n\n* x\n")
        _, out = self.run_cli("evidence", "--log", "scrum")
        self.assertIn("SKIP - no evidence yet today", self.day_block(out, "2026-11-16"))
        self.assertIn("SKIP - non-working day", self.day_block(out, "2026-11-15"))

    def test_S21_has_entry_rereads_the_file(self):
        _, out = self.run_cli("has-entry", "--log", "scrum", "2026-11-12")
        self.assertEqual(out.strip(), "ABSENT")
        self.write_log("scrum", "# Daily\n\n## 2026-11-12\n\n* x\n")
        _, out = self.run_cli("has-entry", "--log", "scrum", "2026-11-12")
        self.assertEqual(out.strip(), "EXISTS")
        self.write_log("team", "# T\n\n## 2026-11-12\n_Provisional — as of 10:00 PKT_\n")
        _, out = self.run_cli("has-entry", "--log", "team", "2026-11-12")
        self.assertEqual(out.strip(), "PROVISIONAL")


class GitEvidence(Fixture):
    def test_S3_stash_is_never_work(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-12")
        self.assertNotIn("index on dev", out)
        self.assertNotIn("On dev: wip", out)
        self.assertNotIn("WIP on", out)
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-12")
        self.assertIn("COMMITS (yours, non-merge, by author date): 1", out)     # only "Lead nit"

    def test_S4_own_commits_include_aliases(self):
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-13")
        block = self.day_block(out, "2026-11-13")
        self.assertIn("Alias commit", block)
        self.assertNotIn("Bob c", block.split("PR MERGES")[0])

    def test_S5_only_real_pr_merges_count_and_refreshes_are_ignored(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-11")
        block = self.day_block(out, "2026-11-11")
        self.assertIn("BRANCH REFRESHES ignored (not work): 1", block)
        self.assertNotIn("Merge branch", block)
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-13")
        block = self.day_block(out, "2026-11-13")
        self.assertIn("PR #14 feature/c", block)
        self.assertIn("PR #15 feature/gh", block)          # GitHub wording, owner prefix dropped
        self.assertEqual(se.pr_match("Merge branch 'dev' into feature/x"), None)
        self.assertEqual(se.pr_match("Merge remote-tracking branch 'origin/dev' into feature/x"), None)
        self.assertEqual(se.pr_match("Merged dev into feature/x"), None)

    def test_S6_pr_author_by_commit_count_tie_to_ae_tip_never(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-12")
        block = self.day_block(out, "2026-11-12")
        self.assertRegex(block, r"PR #12 feature/a -> dev at 10:00: author Alice \(3/4 commits; %ae agrees\); "
                                r"merged by Lead Person")                     # tip (refresh by Lead) ignored
        self.assertRegex(block, r"PR #13 feature/b .*author Bob \(2/3 commits; %ae disagrees .*the count wins")
        self.assertIn("REVIEWED AND MERGED PR #12 by Alice", block)
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-13")
        self.assertRegex(self.day_block(out, "2026-11-13"), r"PR #14 feature/c .*author Bob \(1/2 commits, TIE")
        _, out = self.run_cli("pr-authors", run_git(self.repo, "log", "-1", "--format=%H", "--grep", "pull request #12").strip())
        self.assertIn("AUTHOR Alice", out)
        self.assertIn("Alice: 3/4 (75%) - listed (>=20%)", out)

    def test_S7_open_or_merged_is_judged_at_end_of_that_day_first_parent(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-10")
        block = self.day_block(out, "2026-11-10")
        self.assertIn("branch feature/a, landed by PR #12 on 2026-11-12; not yet merged at end of day", block)
        self.assertNotIn("Add packing list\n    branch feature/a, landed by PR #12 on 2026-11-12; in dev", block)

    def test_S8_commit_placement(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-10")
        self.assertIn("direct to dev, no PR; in dev by end of day", self.day_block(out, "2026-11-10"))
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-13")
        self.assertIn("open on feature/open; not yet merged at end of day", self.day_block(out, "2026-11-13"))

    def test_S16_unmapped_authors_and_no_activity(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-13")
        self.assertIn('UNMAPPED Carol <carol@x.test> -> suggest adding "carol@x.test"', out)
        self.assertIn("NO ACTIVITY: Dana", self.day_block(out, "2026-11-13"))
        self.assertIn("DEV Carol", out)
        order = [m.group(1) for m in re.finditer(r"^DEV (.+)$", self.day_block(out, "2026-11-13"), re.M)]
        self.assertEqual(order[-1], "Carol")              # unmapped after the mapped roster
        nomap = self.tmp / "nomap.json"
        nomap.write_text(json.dumps({"directory": str(self.logs)}))
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-13", config=nomap)
        self.assertIn("no authors map", out)
        self.assertIn("NO ACTIVITY:", out)

    def test_S23_build_output_left_out_of_file_counts(self):
        _, out = self.run_cli("evidence", "--log", "team", "2026-11-10")
        self.assertIn("files: 1 (src 1), 1 build files left out", out)
        self.assertEqual(se.file_summary(["obj/x.cs", "package-lock.json"]), "files: none outside build output")

    def test_scrum_role_in_pr_is_never_guessed(self):
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-13")
        self.assertIn("your role: unknown", self.day_block(out, "2026-11-13"))
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-12")
        self.assertIn("your role: co-author+merger", self.day_block(out, "2026-11-12"))

    def test_merges_command_lists_pr_merges_on_the_integration_branch(self):
        _, out = self.run_cli("merges", "--since", "2026-11-01")
        self.assertEqual(len(re.findall(r"^2026-11-1\d \w+  PR #", out, re.M)), 4)
        self.assertNotIn("Merge branch", out)


class ConfigAndSafety(Fixture):
    def test_S17_output_inside_repository_is_blocked(self):
        code, out = self.run_cli("evidence", "--log", "scrum", "today", extra=("--dir", str(self.repo / "notes")))
        self.assertEqual(code, 2)
        self.assertIn("BLOCK", out)
        self.assertNotIn("===", out)

    def test_S18_git_allow_list_and_no_writes(self):
        g = se.Git(self.repo)
        for bad in (("commit", "-m", "x"), ("checkout", "dev"), ("branch", "-D", "feature/a"),
                    ("config", "user.name", "x"), ("worktree", "add", "x"), ("push",), ("fetch",), ("stash",)):
            with self.assertRaises(se.GitError, msg=bad):
                g.run(*bad)
        source = (HERE / "standup_evidence.py").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"write_text|write_bytes|mkdir|open\([^)]*['\"][wax]\+?['\"]", source))
        before = (run_git(self.repo, "status", "--porcelain"), run_git(self.repo, "stash", "list"),
                  run_git(self.repo, "for-each-ref"), sorted(p.name for p in self.logs.iterdir()))
        for argv in (("status", "--log", "scrum"), ("status", "--log", "team"), ("status", "--log", "history"),
                     ("evidence", "--log", "scrum"), ("evidence", "--log", "team", "last", "week"),
                     ("merges",), ("deploys",)):
            self.run_cli(*argv)
        after = (run_git(self.repo, "status", "--porcelain"), run_git(self.repo, "stash", "list"),
                 run_git(self.repo, "for-each-ref"), sorted(p.name for p in self.logs.iterdir()))
        self.assertEqual(before, after)

    def test_S22_config_resolution(self):
        cfg = self.tmp / "c22.json"
        cfg.write_text(json.dumps({"directory": "~/x/{project}/scrum"}))
        s = se.resolve_settings(str(self.repo), cfg, None)
        self.assertEqual(s.directory, Path.home() / "x" / "Proj-Repo" / "scrum")
        self.assertEqual(s.integration, "dev")
        cfg.write_text(json.dumps({"projectNames": {str(self.repo): "Nice-Name"},
                                   "deployment": {"integrationBranch": "trunk"}}))
        s = se.resolve_settings(str(self.repo), cfg, str(self.tmp / "once"))
        self.assertEqual(s.project, "Nice-Name")
        self.assertEqual(s.directory, self.tmp / "once")
        self.assertEqual(s.file("scrum").name, "Nice-Name-Daily-Updates.md")
        self.assertEqual(s.integration, "trunk")
        self.assertIsNone(se.Repo(se.Git(self.repo), s, se.Clock(se.parse_now(NOW), s.tz)).int_ref)
        missing = se.resolve_settings(str(self.repo), self.tmp / "absent.json", None)
        self.assertEqual(missing.directory, Path.home() / ".claude" / "daily-scrum-updates")


class Transcripts(Fixture):
    def test_S19_prompts_bucketed_and_filtered(self):
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-12")
        block = self.day_block(out, "2026-11-12")
        self.assertIn("Late night prompt counts for the 12th", block)       # 20:00Z on the 11th = 01:00 PKT
        self.assertIn("> Review PR 12 please", block)
        self.assertIn("> /commit now", block)
        self.assertIn("title: Review the packing PR", block)
        self.assertIn("< Done: PR 12 reviewed and merged.", block)
        self.assertRegex(block, r"\[cut: \d+ more chars\]")
        for hidden in ("hidden reminder", "TOOL OUTPUT", "SIDECHAIN", "META SHOULD", "COMPACT SHOULD", "API ERROR"):
            self.assertNotIn(hidden, block)
        self.assertEqual(block.count("> Review PR 12 please"), 1)          # a resumed session's copy counts once
        self.assertIn("> Resumed session prompt", block)
        _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-12", extra=())
        self.assertIn("TRANSCRIPTS " + se.slug(self.repo), out)

    def test_S19_worktree_slugs_and_deduped_roots(self):
        wt = self.tmp / "wt-one"
        run_git(self.repo, "worktree", "add", "-q", str(wt), "feature/gh")
        try:
            d = self.projects / se.slug(wt)
            d.mkdir()
            (d / "wt.jsonl").write_text(jl(type="user", timestamp="2026-11-13T05:00:00Z", cwd=str(wt),
                                           message={"role": "user", "content": "Worktree prompt"}), encoding="utf-8")
            s = se.resolve_settings(str(wt), self.config, None)
            self.assertEqual(s.project, "Proj-Repo")                  # the main repo's name, not the worktree's
            files, dirs = se.transcript_files(s, se.project_roots([str(self.projects), str(self.projects)]))
            self.assertIn(se.slug(wt), dirs)
            self.assertEqual(len(files), len({str(f) for f in files}))
            _, out = self.run_cli("evidence", "--log", "scrum", "2026-11-13")
            self.assertIn("Worktree prompt", out)
        finally:
            shutil.rmtree(self.projects / se.slug(wt), ignore_errors=True)
            run_git(self.repo, "worktree", "remove", "--force", str(wt))

    def test_S19_missing_transcripts_said_plainly(self):
        out = io.StringIO()
        se.main(["--repo", str(self.repo), "--config", str(self.config), "--now", NOW,
                 "--projects-dir", str(self.tmp / "nowhere"), "status", "--log", "scrum"], out=out)
        self.assertIn("unavailable", out.getvalue())


class DeployLedger(Fixture):
    def test_S20_both_wordings_exclusions_dedupe_and_no_hosts(self):
        _, out = self.run_cli("deploys")
        rows = re.findall(r"^DEPLOY .*$", out, re.M)
        text = "\n".join(rows)
        self.assertIn("DEPLOY 2026-11-12 15:00 DEV dev abcdef123456 | smoke passed", text)   # new wording, earliest
        self.assertNotIn("2026-11-13 15:00 DEV dev abcdef123456", text)                     # later duplicate dropped
        self.assertIn("QA dev 1234567 | complete (older report wording)", text)             # old wording
        self.assertIn("QA dev fedcba987654 | smoke skipped", text)
        self.assertIn("DEV feature/x 0123456789ab | smoke FAILED; reverted to 0123456789ab", text)
        self.assertIn("QA qa 5555555aaaaa | smoke passed IN PART", text)                     # raw UTF-8 dash
        self.assertIn("QA - 4444444bbbbb | smoke skipped", text)                      # relayed, no Branch line
        for absent in ("999999999999", "888888888888", "{env}", "7777777", "3333333"):
            self.assertNotIn(absent, text)
        self.assertEqual(len(rows), 6)
        self.assertIn("2 NOT deployed / Deploy FAILED, 1 with no verdict line above", out)
        self.assertRegex(out, r"CANDIDATE 2026-11-14 17:00 DEV dev 3333333 \| no verdict line above it")
        for leak in ("10.9.8.7", "deployer", "/srv", "8080"):
            self.assertNotIn(leak, out)
        self.assertIn("WATERMARK transcripts<=", out)
        _, later = self.run_cli("deploys", "--since", "2026-11-13T23:00:00Z")
        self.assertEqual(len(re.findall(r"^DEPLOY ", later, re.M)), 2)          # the two on the 14th


if __name__ == "__main__":
    unittest.main()
