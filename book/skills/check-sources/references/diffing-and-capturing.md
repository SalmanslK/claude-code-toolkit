# Diffing a moved source, and capturing it

Loaded by [`../SKILL.md`](../SKILL.md) only once Phase 2's fingerprint says a source moved.
PDF reading follows [Reading the FSD](../../fact-check/references/reading-the-fsd.md): print,
never write — the guard refuses `pdftotext` with an output file.

## Text documents and PDFs — fingerprint by counts

`$OLD` is the committed `V<n>.pdf`; `$NEW` is the download, saved in the session's scratchpad
(never in the repository) until Phase 4 captures it. Compare page count, line count and total
characters, without writing either extraction (paragraph and table counts, where the two
extractions keep them, corroborate):

```bash
for f in "$OLD" "$NEW"; do echo "pages $(pdftotext -raw "$f" - | tr -cd '\f' | wc -c)"; pdftotext -raw "$f" - | wc -lc; done
```

Every count matching means that source almost certainly has not moved — say so and go on. **`-raw`,
not `-layout`**, when comparing: `-raw` keeps reading order; `-layout` scrambles merged table cells.

## When a live connector is available

**The table of contents is not sufficient on its own.** V7's TOC matched V6 exactly — 192/192
entries, same titles, same page numbers — while the live Doc had grown by 10,268 bytes inside two
existing sections. **`modifiedTime` and `fileSize` moving is what to act on.** If either moved
since the last capture, pull the full live content and diff it against the previous live pull if
one is saved from an earlier session, otherwise against the last committed `V<n>.pdf` — noisier
(different extraction, different line-wrapping) but it still catches a real content difference.
Save each live pull's text in the session's scratchpad (it is the connector's own tool output,
not a `pdftotext` file), then:

```bash
git diff --no-index --unified=1 "<scratchpad>/fsd-live-previous.txt" "<scratchpad>/fsd-live-current.txt"
```

## The diff

```bash
diff -U2 <(pdftotext -raw "$OLD" -) <(pdftotext -raw "$NEW" -)
```

**Expect noise.** Page numbers extract inline, so a paragraph shifting across a page boundary shows
as a two-line move with no content change — roughly two-thirds of the raw diff. Read past it.

**Measure section sizes as well as reading the diff.** Count the lines between each body heading
and the next, in both versions. The diff alone under-reports scale and hides removals:

- **A section that grew from 1 line to 171 looks like an unremarkable run of additions.** V4's
  largest change — §2.13.8 going from an empty heading to a full specification — was first
  written up as a *rename*.
- **A section that shrank is invisible.** V4 deleted a rule from §2.13.6 that nothing in the
  hunks made stand out.
- **"Nothing outside §X moved" is a claim to verify, not to infer.** V4 also changed §2.12.3,
  which the first pass missed while asserting the opposite.

**Match headings in the body, not the table of contents** — filter out lines with `....` and skip
the front matter, or every section looks empty.

Sort real changes into the categories `docs/project.md` Part 3 uses:

1. **New requirements** — sections that did not exist
2. **Corrections to wrong text** — a rule whose meaning changed
3. **Renames and rewording** — same meaning, different words
4. **What did *not* change** — especially sections we are waiting on. **"§2.13.10 is still empty"
   is a finding**, and the one that affects the schedule.

## Capturing the download

**Decode straight to disk, never through an intermediate text file.** A Google Doc's PDF export
comes back as base64 in the tool result; write it with a script that reads the tool's own saved
JSON output and decodes directly to the destination path. Re-pasting base64 through the Write tool
once produced a file with the right byte count that failed to unzip with a bad CRC.

**Verify every capture:** a PDF must open with `pdftotext … -`, an `.xlsx` must unzip cleanly,
and the specific text the diff found must be present in the saved file.
