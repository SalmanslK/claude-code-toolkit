# dev-deploy

**F2 · Releases and status.** **Trigger:** a merged fix onto DEV.
**Packs:** deploy.

## Steps

1. ✋ `/deploy DEV` — the full suite may be skipped for a quick fix; the report says so.
2. ✋ `/book:raise defect` — if the post-deploy smoke fails: keep or revert first, then raise it.

## Done when

DEV runs the commit and the smoke passed, or the failure is raised.
