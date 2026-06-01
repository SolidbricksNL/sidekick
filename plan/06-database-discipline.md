# Database discipline

**Status:** not started
**Depends on:** 04-project-model-and-scaffolding, 05-write-disciplines-enforcement

## Goal
"Done" means the SQLite layer is finalized: when to use the database vs the
brain; the "extend before add" rule; the plain-language schema-change
confirmation; `brain/data-model.md` as the human-readable schema knowledge; and
precise lazy-creation behavior. The acceptance artifact is a **worked example**
on a small sample project showing a first table proposed in plain language,
created, documented in `data-model.md`, then later extended with a new column —
every structural step passing through the plain-language gatekeeper, while
record inserts flow freely.

## Context
- `ARCHITECTURE.md` §4 (database layer).
- `skills/sidekick/references/database-discipline.md` (full protocol).
- `skills/sidekick/SKILL.md` ("The database, in brief").
- Gatekeeper rule from plan 05; `data-model.md` lives in `brain/` (plan 07).

## Tasks
1. [ ] Confirm the brain-vs-database boundary is crisp: prose/decisions → brain;
   queryable repeating records → database. Restate the signals for "use the
   database" (a list of similar items; recurring fields; how-many/which/sorted
   questions).
2. [ ] Confirm the three principles are stated: Sidekick designs tables; extend
   before add; schema-as-knowledge in `brain/data-model.md`.
3. [ ] Confirm the gatekeeper covers exactly the structural operations (create
   table, add/remove/rename column, change a column's meaning) and that reading
   + inserting records that fit are explicitly free.
4. [ ] Confirm lazy creation: `data.sqlite` is NOT made at scaffold; the first
   table creation is itself a structure change and must be confirmed in plain
   language.
5. [ ] Implement the **execution mechanism**: Sidekick runs SQL via Python's
   stdlib `sqlite3` module through a small helper script bundled in the plugin
   (e.g. `skills/sidekick/scripts/db.py`) — NOT the `sqlite3` CLI (not present
   in-env and not guaranteed in Cowork). The helper supports exactly what the
   discipline needs: run a schema statement (after approval), insert records that
   fit, and run a read query. Per-project databases stay at
   `projects/<slug>/data.sqlite`. Create the helper in this unit and document how
   the skill invokes it (`python3 <helper> ...`).
6. [ ] Build the **worked example** (write it into this plan as the artifact):
   - User shares a list of contacts → Sidekick proposes a `contacts` table in
     plain language ("Shall I start a contact list with name, company, role,
     email?") → on yes, create table + write `brain/data-model.md`.
   - User adds more contacts → records inserted freely, no prompt.
   - Later the user shares phone numbers → plain-language proposal to add a
     `phone` field → on yes, alter + update `data-model.md` with the dated
     column note.
   - Show the `brain/data-model.md` content at each step (matching the format in
     `database-discipline.md`).
7. [ ] Confirm `data-model.md` format guidance is followed (one section per
   table, column→meaning table, typical queries, dated column additions).
8. [ ] Confirm query hygiene rules (explicit columns, summarize-in-chat, large
   extracts to `log/`, an exported sheet is an `output/` action needing
   confirmation).

## Acceptance criteria
- A written worked example exists showing: first-table proposal (plain
  language) → creation → `data-model.md` documentation → free record inserts →
  later column addition (plain language) → `data-model.md` update.
- Lazy-creation behavior is unambiguous and the first table is gated.
- "Extend before add" is demonstrated, not just asserted.
- The SQLite execution mechanism assumption is documented (or raised as an open
  question for the user).

## Notes / open questions (SQLite mechanism resolved 2026-06-01)
- **SQLite execution — RESOLVED.** Sidekick runs SQLite via Python's stdlib
  `sqlite3` module (Python 3.11 confirmed in-env; the `sqlite3` CLI is NOT
  present and not guaranteed in Cowork). A helper script bundled in the plugin
  performs create/alter/query; no external dependency. Node 24 is also available
  as a fallback runtime if ever needed. Per-project DBs live at
  `projects/<slug>/data.sqlite` (in the workspace, not the plugin).
- **Schema in two places.** The schema lives both in the actual `data.sqlite`
  and (in plain language) in `brain/data-model.md`. Note the risk of drift and
  the rule that `data-model.md` is updated in the same approved step as the
  structure change.
