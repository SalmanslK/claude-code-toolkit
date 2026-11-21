# When the connector cannot open a document

Loaded by [`../SKILL.md`](../SKILL.md) Phase 1 only when a Drive read fails.

A connector can return "not found" for the FSD Doc and the matrix Sheet while other files open
by direct id in the same session. Once it has worked, **a failure is a regression from a known-good state** — diagnose
it the same way, and say plainly that it used to work.

"No access" and "no such file" look identical, so diagnose before reporting:

1. **Retry by a second call** — metadata *and* content read. One failure could be transient;
   two by different routes is not.
2. **Confirm the mechanism works** by opening a file you can reach. If another direct-id lookup
   succeeds in the same session, the connector is fine and the problem is that document.
3. **Check the account** — search `owner = '<the person's address>'`. If their own files come
   back, the connector is on the right account and access is the issue.
4. **A `search_files` miss proves nothing.** Search indexed none of these documents, including
   ones that open perfectly by id. Never conclude "not shared" from a search returning nothing.

**Being able to open a document in a browser does not mean the API can fetch it.** The user
could view both the FSD and the matrix in the browser while metadata, content read and export
all returned "not found" for the same ids. So **never diagnose this as "you don't have
access"**. The two explanations that fit are both invisible from the browser:

- **The file lives in a Shared Drive.** The Drive API returns 404 for shared-drive items unless
  the caller opts into shared-drive support.
- **The owning organisation restricts third-party app access.** A Workspace admin can allow-list
  which apps reach their data.

Neither is fixable from this end, and neither is the user doing something wrong. **Stop and
ask the person for the manual export** rather than sending them to hunt through sharing
settings that are already correct:

> File → Download → **PDF** for a Doc, **CSV** for a Sheet.

Copying the file into the person's own Drive would make it API-readable and is the wrong
answer — **a copy stops tracking the live document**, which is the one property the skill
depends on.

> **Always take CSV for a Sheet, never the PDF.** The matrix PDF does not extract reliably: a
> spreadsheet export with merged cells, where `pdftotext` misaligns the Yes/No values against
> the wrong features. **That has already produced one false "contradiction" finding.** Never
> transcribe from PDF text.
