---
name: update-erd
description: >
  Use after a schema change (migration, entity or table change) to update the entity-relationship
  documentation: reads the current schema, diffs it against the documented ERD, and updates the diagram
  and table notes. Keeps the ERD a true picture of the database.
---

# Update the ERD

1. **Read the schema** from the source of truth: migrations or entity configuration, or the live
   database's catalogue when the user provides access. Prefer code over a live database.
2. **Read the documented ERD** (`docs/erd.md`, or the path the project names): tables, columns, keys,
   relationships.
3. **Diff**: tables/columns added, removed, renamed, retyped; keys and indexes; relationship changes
   (cardinality, nullability, delete behaviour).
4. **Update** the diagram (Mermaid `erDiagram` by default) and the per-table notes. Keep unchanged parts
   byte-for-byte. Record destructive changes (drops, narrowing types) under a *Watch* heading.
5. **Verify** every table in the doc exists in the schema and vice versa; list any mismatch left.
6. **Report** the diff and the files changed. Do not edit migrations or code.
