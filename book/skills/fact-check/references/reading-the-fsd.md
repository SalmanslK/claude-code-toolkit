# Reading the FSD

**Shared by every skill and agent that quotes the FSD** — `/book:fact-check`, `/book:self-review` and
`/book:peer-review` (Pass A), `/book:check-sources`, `/book:outline-api`. Add a new recipe here, not
to any of them.

**Which file.** `requirements/fsd/… - V<n>.pdf` with the highest `n` **numerically** — the
`FSD=` line below; a lexical sort puts `V9` above `V17`. The filename is the only version marker.

**Print, never write.** The guard refuses `pdftotext` unless its last argument is `-`, including
`- > file`. Every recipe below prints or pipes; none leaves a file behind.

**Read the section, not the document.** The FSD is hundreds of pages; a requirement needs one or
two. Locate, then print only those pages — **`book fsd-page` does both**:

```bash
python3 devtools/book.py fsd-page "Log In"           # the highest V<n>, its pages, the command to print them
python3 devtools/book.py fsd-page "Log In" --print   # and those pages' text
```

It takes the heading as the contents print it (the FSD has no section numbers), finds it in the
text after the contents, and spans to the next heading at its level; a repeated sub-heading
(*Flow of Events*) is listed under each parent. A heading it cannot find — garbled, renamed, not
in the contents — is reported as not found and the command fails: **never guess a page**. It
only reads (pdftotext printing to `-`), and without pdftotext it says so and prints the PDF's path.

By hand, when the command cannot help:

```bash
FSD="requirements/fsd/$(ls requirements/fsd | grep -E 'V[0-9]+\.pdf$' | sort -V | tail -1)"

# 1. Which PDF page holds the heading (skips the table of contents' dot leaders):
pdftotext -layout "$FSD" - | awk '{pg+=gsub(/\f/,"")} /^ *Log In *$/ && !/\.\.\.\./ {print "page " pg+1 ": " $0}'

# 2. Print those pages:
pdftotext -layout -f 13 -l 14 "$FSD" -
```

The page either prints is the PDF's page index, for `-f`/`-l` — not the number printed in the
table of contents. `-layout` keeps tables aligned for reading a section; `-raw` keeps reading
order for diffing two revisions.

**Two revisions, without a file** — each `pdftotext` prints into the comparison:

```bash
diff -U2 <(pdftotext -raw "$OLD" -) <(pdftotext -raw "$NEW" -)
```

**Cite** the section number **and** heading text. Where the PDF's numbering is garbled, say so
and cite page + heading — never adopt a plan's reading of the FSD's structure.

**Already read in this session?** Quote what you read; re-read only if the file or the section
changed.

**Permissions come from the FSD** — no permissions matrix exists (CLAUDE.md *Layout*). If one is
ever shared, never read its PDF: merged cells misalign under `pdftotext`; read its Sheet as CSV.
