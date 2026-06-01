# Database discipline

**Status:** done (db.py helper built + verified; worked example written)
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
1. [x] Confirm the brain-vs-database boundary is crisp: prose/decisions → brain;
   queryable repeating records → database. Restate the signals for "use the
   database" (a list of similar items; recurring fields; how-many/which/sorted
   questions).
2. [x] Confirm the three principles are stated: Sidekick designs tables; extend
   before add; schema-as-knowledge in `brain/data-model.md`.
3. [x] Confirm the gatekeeper covers exactly the structural operations (create
   table, add/remove/rename column, change a column's meaning) and that reading
   + inserting records that fit are explicitly free.
4. [x] Confirm lazy creation: `data.sqlite` is NOT made at scaffold; the first
   table creation is itself a structure change and must be confirmed in plain
   language.
5. [x] Implement the **execution mechanism**: Sidekick runs SQL via Python's
   stdlib `sqlite3` module through a small helper script bundled in the plugin
   (e.g. `skills/sidekick/scripts/db.py`) — NOT the `sqlite3` CLI (not present
   in-env and not guaranteed in Cowork). The helper supports exactly what the
   discipline needs: run a schema statement (after approval), insert records that
   fit, and run a read query. Per-project databases stay at
   `projects/<slug>/data.sqlite`. Create the helper in this unit and document how
   the skill invokes it (`python3 <helper> ...`).
6. [x] Build the **worked example** (write it into this plan as the artifact):
   - User shares a list of contacts → Sidekick proposes a `contacts` table in
     plain language ("Shall I start a contact list with name, company, role,
     email?") → on yes, create table + write `brain/data-model.md`.
   - User adds more contacts → records inserted freely, no prompt.
   - Later the user shares phone numbers → plain-language proposal to add a
     `phone` field → on yes, alter + update `data-model.md` with the dated
     column note.
   - Show the `brain/data-model.md` content at each step (matching the format in
     `database-discipline.md`).
7. [x] Confirm `data-model.md` format guidance is followed (one section per
   table, column→meaning table, typical queries, dated column additions).
8. [x] Confirm query hygiene rules (explicit columns, summarize-in-chat, large
   extracts to `log/`, an exported sheet is an `output/` action needing
   confirmation).

## Resolution (2026-06-01)

### Protocol confirmations (tasks 1–4, 7, 8)

- **Brain vs database boundary (task 1)** — crisp in `database-discipline.md`:
  prose/decisions → brain ("the BPD contract renews annually"); queryable
  repeating records → database ("142 contacts, each with name/company/role/
  email"). "Use the database" signals are stated: a list of similar items;
  recurring fields; how-many / which / sorted questions. ✓
- **Three principles (task 2)** — all present: Sidekick designs tables; extend
  before add; schema-as-knowledge in `brain/data-model.md`. ✓
- **Gatekeeper scope (task 3)** — covers exactly the structural ops (create
  table, add/remove/rename column, change a column's meaning); reading and
  inserting records that fit are explicitly free. ✓
- **Lazy creation (task 4)** — `data.sqlite` is not made at scaffold (plan 04
  contract); the first table creation is itself a confirmed structure change.
  The helper's `schema` call is the concrete lazy-creation point (verified:
  `info` before any `schema` reports `exists:false`). ✓
- **`data-model.md` format (task 7)** — one section per table, column→meaning
  table, typical queries, dated column additions; matched in the worked example
  below. ✓
- **Query hygiene (task 8)** — explicit columns over `SELECT *`, summarize in
  chat / large extracts to `log/`, an exported sheet is an `output/` action
  needing confirmation. ✓

### Execution mechanism (task 5) — IMPLEMENTED

Built `skills/sidekick/scripts/db.py` (Python stdlib only; no `sqlite3` CLI
dependency, per resolved decision 3). Subcommands: `schema` (one approved DDL,
lazily creates the DB + parent dir), `insert` (parameterized; records that
fit), `query` (opens the DB **read-only** so a read cannot mutate), `info`
(tables + columns, for extend-before-add and regenerating `data-model.md`). The
helper executes SQL but does **not** enforce the gatekeeper — the skill must get
plain-language approval before any `schema` call. Invocation documented in
`database-discipline.md` ("Running SQL (the bundled helper)").

**Verified in-env** (Python 3.11.9), full sequence exit 0:
- `info` before any table → `exists:false` (lazy).
- `schema` CREATE contacts → ok.
- `insert` 3 contacts → `inserted:3` (no prompt).
- `query` "contacts without email" (read-only conn) → 1 row (Alan Turing).
- `schema` ALTER ADD COLUMN phone → ok.
- `info` after → contacts now has the `phone` column.

**Safety, verified:** a write attempted through `query` fails
(`attempt to write a readonly database`, exit 1); `insert` into a non-existent
DB errors (create the table first); a malicious table identifier (`t;DROP`) is
rejected before any SQL runs.

### Worked example (task 6) — propose → create → document → extend

**1. User shares a list of contacts.** Sidekick recognizes a repeating shape and
asks in plain language (multiple choice per the interaction style):

> "Shall I start a contact list with **name, company, role, email**?"
> → Yes / Adjust fields / Not now

On **Yes**, create the table (the first structure change = confirmed):

```
python3 scripts/db.py schema --db projects/acme/data.sqlite \
  --sql "CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, company TEXT, role TEXT, email TEXT)"
→ {"ok": true, "action": "schema", ...}
```

…and write `brain/data-model.md` in the **same approved step**:

```markdown
# Data model

_Last updated: 2026-06-01_

## contacts
People we deal with in this project.

| column  | meaning                     |
|---------|-----------------------------|
| id      | unique id                   |
| name    | full name                   |
| company | organization they belong to |
| role    | their job title             |
| email   | primary email               |

Typical queries: list all contacts at a given company; find contacts
without an email.
```

**2. User adds more contacts.** Records that fit flow in freely — no prompt:

```
python3 scripts/db.py insert --db projects/acme/data.sqlite --table contacts \
  --json '[{"name":"Ada Lovelace","company":"Analytical","role":"Engineer","email":"ada@ex.com"}, …]'
→ {"ok": true, "action": "insert", "table": "contacts", "inserted": 3}
```

A read summarizes in chat (large extracts would go to `log/`):

```
python3 scripts/db.py query --db projects/acme/data.sqlite \
  --sql "SELECT name, company FROM contacts WHERE email IS NULL"
→ {"ok": true, "rowcount": 1, "rows": [{"name":"Alan Turing","company":"NPL"}]}
```

**3. User later shares phone numbers.** This is a structure change → plain
language first, and **extend before add** (a column on `contacts`, not a new
table — confirmed via `info` showing `contacts` already holds the people):

> "You're now also tracking **phone numbers** for contacts. Shall I add a
> **phone** field to the contact list?" → Yes / No / Explain first

On **Yes**, alter and update `data-model.md` in the same step:

```
python3 scripts/db.py schema --db projects/acme/data.sqlite \
  --sql "ALTER TABLE contacts ADD COLUMN phone TEXT"
→ {"ok": true, "action": "schema", ...}
```

`brain/data-model.md` gains one dated row (the rest unchanged):

```markdown
| phone   | primary phone (added 2026-06-01) |
```

Every structural step passed the plain-language gatekeeper; every record insert
and read flowed freely. Extend-before-add was demonstrated, not just asserted.

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
