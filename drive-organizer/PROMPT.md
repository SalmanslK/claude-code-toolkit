# Kickoff prompt (paste into Claude Code on the new computer)

First copy the `drive-organizer` folder to `~/.claude/skills/drive-organizer/`
(so `SKILL.md`, `PLAN.md`, `PROMPT.md`, `helpers.ps1` sit together), then start
Claude Code in the root of the drive you want to organize, and paste:

---

Use the `drive-organizer` skill to audit and organize **<D:\ | C:\Users\<me>\Desktop, Downloads, Documents | both>**.

Follow the skill's phases and rules exactly. In particular:

- **Phase 1 now, read-only:** inventory the folders, find git repos and worktrees,
  duplicates (same SHA-256), zips that are already extracted, stale shortcuts and
  empty folders. Summarize per folder; do not dump huge listings.
- **Phase 2:** write `PLAN.md` in a new `_Drive-Audit-<today>` folder at the drive root and show me
  a short version: problems found, the proposed structure (keep it small and based on what exists),
  what you will leave untouched, and the risks. **Stop and wait for my approval.**
- After I approve: execute in small batches with the helper functions, log every move, put deletion
  candidates in `To Delete - Review Before Deletion` with a manifest (never delete anything yourself),
  verify, and write `REPORT.md`.

Constraints:

- Do not move git repositories or git worktrees. Do not touch app-managed folders.
- Do not print any password, key, token or signed URL. Compare credential files by value in memory
  and merge them into one `.txt` per project only after I approve.
- Anything you can't identify confidently goes to `Work\Inbox\Unsorted` — ask me before guessing.
- After each phase, give me a short status and a recommendation with each question.

Things about me/this computer you should know first:
<fill in: my work (clients/projects), folders that must not move, apps that depend on specific paths,
 whether OneDrive redirects Desktop/Documents, preferred folder naming style>

---

## Optional follow-up prompts

- *Desktop / Downloads / Documents pass:*
  "Do the same for my Desktop, Downloads and Documents. Move files onto the data drive where they
  belong, fix any shortcut that points at a moved folder, and leave app-managed folders alone."
- *Inbox triage:*
  "Open the files in `Work\Inbox` (images, documents, data files), work out what each belongs to,
  and file them. Tell me which ones you still can't identify."
- *Credentials:*
  "Merge my plain-text credential files into one `.txt` per project without printing any values;
  verify 0 values are missing from the merged file; then move the originals to the review folder."
- *Password manager:*
  "Prepare a Bitwarden-format CSV from the merged credential files without printing values.
  I'll import it and delete the CSV and the .txt files."
- *Final check:*
  "Run Phase 4 verification and update REPORT.md with what is still open."
