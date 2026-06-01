# Brain protocol (`brain/`)

The per-project memory protocol. Loaded on demand by the `sidekick`
skill. Derived from the "Setting up a project brain" method, scoped to a
single project under `projects/<slug>/`.

## What the brain is

The brain is the project's permanent knowledge memory. It solves the
problem that the chat forgets everything when the session closes. The
brain remembers: it grows with every document fed into it, and Sidekick
reads it at the start of every session as background.

Three file layers per project, each with a different lifespan — do not
confuse them:

| Layer | Folder | Lifespan | Purpose |
|---|---|---|---|
| **Memory** | `brain/` | Permanent | Distilled, durable knowledge — what to *remember*. |
| **Log** | `log/` | Ongoing | Structured logbook of the work process. |
| **Output** | `output/` | Long | Clean deliverables to keep or share. |
| **Archive** | `archive/` | Reference | Processed source files (originals), kept for reference. |

There is **no inbox folder.** Input arrives through the chat. When the
user shares a document in a session, that *is* the inbox.

The golden rule: **what is shared in the chat is distilled into `brain/`,
the original goes to `archive/`, work-in-progress is recorded in `log/`,
and only clean deliverables go to `output/`.**

## Filling the brain — by distillation

### Step 1 — Input arrives in the chat

Anything relevant — a document, a note, an article, a report — is shared
in the chat. That is the entry point; there is no separate folder to dump
into.

**Fork on the input's shape first.** If what arrives is **tabular or
repeating-record data** (a spreadsheet, CSV, exported table, a list of
same-shaped items), the rows do **not** belong in the brain or a log —
propose a **database table** and load them (see `database-discipline.md`).
Only the prose *insights* drawn from that data follow the brain
distillation below. For free-form prose, notes, and reports, continue with
Step 2.

### Step 2 — Distill into `brain/`

Processing is **not copying** — it is summarizing to the essence:

1. Read the shared document.
2. Extract the key points — the essence, not the raw text.
3. Add those to the right brain file (or update an existing line).
4. Keep the original source file in `archive/` for reference.
5. **Show a diff of the change first; write only after approval.**

For a brand-new brain file, the whole file is the diff — show the full
proposed content. For an edit, show only the changed line(s) as a plain
before/after, and **amend the existing line; never stack a second,
contradictory version.**

The difference between `archive/` and `brain/`: `archive/` holds the
whole original; `brain/` holds only what must be remembered from it.

### Step 3 — Record the session in `log/`

Alongside distilling into `brain/`, keep a structured logbook in `log/`.
Where `brain/` stores the *result* (durable knowledge), `log/` records
the *process*: which documents were processed this session, which
decisions were made, which deliverables were produced, what open points
remain. One file per session/topic, named `YYYYMMDD-<slug>.md`.

## How to split the brain into files

Start small. One or two files per project is enough to begin. Split only
once a file grows too large or too broad. Typical brain files:

- `<topic>.md` — the central knowledge about the main subject (status,
  decisions, facts).
- `landscape.md` or `overview.md` — an overview of tools, players, or
  options in the field.
- `links.md` — useful URLs with one line of explanation each.
- `decisions.md` — chronological log of decisions (what, why, when).
- `data-model.md` — plain-language description of the SQLite schema (see
  database-discipline.md).

Keep every file **lean and current.** A brain full of outdated or
duplicate information becomes worthless.

## Four rules for a healthy brain

1. **Distill, don't copy.** The essence belongs in the brain, not raw
   text.
2. **Always show a diff.** Write changes only after explicit approval —
   this keeps control and prevents noise creeping in.
3. **No new files without asking.** Prevents sprawl and fragmentation.
4. **Update existing lines instead of adding.** When a fact changes,
   amend the existing line — don't stack contradictory versions.

## Using the brain

### At session start: read as background

Read the relevant brain files at the start of a session, so you have
immediate context — what's going on, which decisions are made, what the
status is — without the user re-explaining. The project's `CLAUDE.md`
lists which files to read.

### During the work: log it in `log/`

Substantive work is recorded in `log/`, not just in the chat. The chat is
for short questions, decisions, and alignment. The chat has limited
memory; the log persists. The chat is the steering wheel, the log is the
workbench.

### After the work: write back to the brain

What was decided or learned during a session is written back to `brain/`
so the next session benefits. The log records that it happened; the brain
keeps the durable essence. This is the cycle that lets the system grow.

**Safety net — undistilled logs are not lost.** If the inline write-back is
missed, the loop still closes: the **check-in** scans each project's `log/` for
files lacking a `> distilled to brain:` stamp, distills each (diff + approval),
and then stamps the log. (The triage only reports an undistilled-log count as a
heads-up.) So a good logged discussion always gets a chance to reach the brain,
even sessions later.

## The cycle in one glance

```
SHARE IN CHAT   → share a document in the session (replaces the inbox)
  ↓
DISTILL         → key points into brain/, original into archive/ (diff + approval)
  ↓
LOG             → record the session in log/ (free, no permission)
  ↓
USE             → read brain/ at session start as context
  ↓
DELIVERABLE     → clean deliverables in output/ (confirmation)
  ↓
WRITE BACK      → new insights and decisions back into brain/
```
