---
name: role-permissions-matrix
description: >
  Use to design, document or audit role-based permissions: builds the role × action matrix from the
  requirements, compares it with what the code enforces, and lists gaps. Use before changing roles and
  when a role-related defect appears.
---

# Role-based permissions matrix

1. **Collect the roles and actions.** Roles from the requirements and the code's role definitions;
   actions as `resource.verb` (for example `order.create`, `order.approve`). One row per action.
2. **Build the intended matrix** from the requirements: role × action → allow / deny / own-records-only.
   Where the requirements are silent or contradict themselves, mark `?` and raise a question; do not
   choose.
3. **Read the enforcement** in the code (attributes, policies, middleware, query filters). Record for each
   action what the code actually allows.
4. **Diff** intended vs enforced. Classify each difference: *missing check* (security gap, top priority),
   *too strict*, *wrong scope* (can see others' records), *undocumented*.
5. **Write** `docs/permissions.md`: the matrix, the gaps ranked, and for each gap the file and line.
   Propose a test per gap (role X calling action Y expects status Z).
6. **Never** weaken a check to make a test pass, and never invent an allow rule. Gaps are reported.
