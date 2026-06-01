# Database discipline (`data.sqlite`)

The full protocol for the per-project SQLite database. Loaded on demand
by the `sidekick` skill.

## Purpose

When information shared in a project is **genuinely structured** —
lists, records, repeating fields, things you would naturally query — it
belongs in a database, not scattered across log files or the brain. Each
project has one SQLite file at `projects/<slug>/data.sqlite`.

The brain holds prose knowledge ("the BPD contract renews annually"). The
database holds queryable records ("142 contacts, each with name, company,
role, email"). Don't put structured records in the brain, and don't put
prose narrative in the database.

## When to use the database

Use it when the information has a clear, repeating shape and the user
will plausibly want to filter, count, sort, or relate it. Signals:

- The user shares or builds a list of similar items.
- The same fields recur across many entries.
- The user asks questions like "how many", "which ones", "sorted by".

Do **not** force unstructured or one-off information into tables. A single
fact is a brain line, not a table.

## Three principles

1. **You design the tables.** Decide the schema yourself, based on the
   actual shape of the data. Choose clear table and column names a
   non-technical person would recognize.
2. **Extend before you add.** When new related information arrives, first
   check whether it fits an existing table (possibly by adding a column)
   before creating a new table. The database must not become a tangle of
   overlapping tables.
3. **Schema as knowledge.** Document every table in plain language in
   `brain/data-model.md` so that you — and the user — can write clear
   queries later without re-inspecting the schema.

## The gatekeeper: structure changes only

**Confirmation is required for structure changes, in plain language.**

A structure change is: creating a table, adding a column, removing a
column, renaming a table or column, or changing a column's meaning.

- Ask in terms the user understands, tied to their data — never SQL.
  - Good: *"You're now also tracking phone numbers for contacts. Shall I
    add a phone field to the contact list?"*
  - Bad: *"ALTER TABLE contacts ADD COLUMN phone TEXT;"*
- Show what will change and why, then wait for approval.
- Only after approval, apply the change and update `brain/data-model.md`.

**No confirmation needed for:**

- **Reading** data (any query).
- **Populating** existing tables with records that fit the existing
  schema. Adding rows is normal use, not a structure change. Do not ask
  permission to insert records that fit.

This keeps the workflow fluid: the user approves the *shape* once, then
data flows in freely.

## `brain/data-model.md` format

Keep it lean and current. One section per table:

```markdown
# Data model

_Last updated: 2026-03-01_

## contacts
Stores people we deal with in this project.

| column   | meaning                                  |
|----------|------------------------------------------|
| id       | unique id                                |
| name     | full name                                |
| company  | organization they belong to              |
| role     | their job title                          |
| email    | primary email                            |
| phone    | primary phone (added 2026-03-01)         |

Typical queries: list all contacts at a given company; find contacts
without an email.
```

When you change the schema, update this file in the same step (after
approval). A reader should be able to write correct queries from this
file alone.

## Query hygiene

- Write clear, readable SQL. Prefer explicit column lists over `SELECT *`
  in anything you keep.
- When you report results to the user, summarize in the chat language;
  put any large extract in `log/`, not the chat.
- If a query result becomes a deliverable (an exported sheet, say), that
  is an `output/` action and needs confirmation.

## Lazy creation

Do not create `data.sqlite` during project scaffolding. Create it the
first time structured data actually needs storing — and that first table
creation is itself a structure change, so confirm it in plain language.
