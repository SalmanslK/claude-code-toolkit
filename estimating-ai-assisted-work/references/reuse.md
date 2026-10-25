# Reuse from a named codebase

**Reuse from an existing codebase: only when the user names one** ("estimate this, reusing what we built in X"). Otherwise skip this; nothing else changes.
- **Group the list into tasks**, the slices above, and keep each task's drivers from its size count.
- **Score each driver against the named codebase.** Search for the endpoint, command, entity or error by name:
  - exists and fits as is: 1;
  - exists but behaves differently or needs changing: ½;
  - not there: 0.
- **Reuse % = the reusable size points ÷ the task's size points**, weighting each driver as in S (endpoints and entities 1, rules and links ½). For a ratio-priced task with no size count, list the pieces it needs and score them the same way.
- **Porting floor (assumed):** copied code still costs 25% of its estimate for wiring, renames and adapting tests. So E_after = E × (1 − 0.75 × reuse %). If the new product calls the source backend directly as a shared service, E_after = E × (1 − reuse %).
- **Apply reuse to min, likely and max alike, and to the bid.** The pooled factor and the per-item buffers then work on E_after.
- **Never average a with-reuse figure with a without-reuse one.** That is a bet on whether reuse happens, not a reduction in error. When reuse depends on an open question (such as the target's stack), show both scenarios and name the question that decides between them.
- **Web and mobile:** reuse counts only if the source has the same kind of client.

