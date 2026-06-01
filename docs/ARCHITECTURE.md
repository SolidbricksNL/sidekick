# Sidekick — Architecture

> Source of truth for the Sidekick Cowork plugin. Every `SKILL.md` in
> this plugin is derived from this document. If you change the design,
> change this document first and then update the skills.

---

## 1. What Sidekick is

Sidekick is a generic, role-adaptive Cowork plugin that gives every
employee a structured, discipline-enforcing work environment. The plugin
adapts to the user's role (Managing Director, client consultant,
marketer, …) and behaves as a personal advisor/assistant for *that*
role.

The core problem Sidekick solves is Cowork's tendency toward sprawl.
Cowork has two opposite habits:

1. **Putting everything in the chat** — which fills the chat and loses
   information at compaction time.
2. **Creating unstructured working documents on every chat** — without
   structure, without findability.

Sidekick fixes this by anchoring everything in a **project** and by
enforcing three strictly separated **write disciplines**.

---

## 2. The central principle: three write disciplines

This is the heart of the plugin. Everything Sidekick writes falls into
exactly one of three categories, each with its own gatekeeper rule:

| # | Category | Where | Gatekeeper | Tone |
|---|----------|-------|------------|------|
| 1 | **Log** (process) | `log/` | **Write freely** — no permission needed | — |
| 2 | **Brain** (memory) | `brain/` | **Show a diff + get approval** | non-technical |
| 3 | **Output** (deliverables) | `output/` | **Ask for confirmation** (create / edit / delete) | non-technical |
| 3b | **Structured data** (structure) | `data/` | **Ask for confirmation** on a table/column change | **non-technical** |

The reasoning: the log is allowed to fill up freely, because that is
exactly where work-in-progress belongs instead of in the chat. The brain
and the output are precious and durable, so the human stands as
gatekeeper there. The data **structure** is sensitive, so table/column
changes are always presented **in plain language** — never as SQL or
technical jargon. Records that fit existing columns flow in freely.

**Rule of thumb for Sidekick itself:** "Before I write anything, I ask
myself: is this log (free), brain (diff + approval), or output/data
(confirmation)?"

---

## 3. The project model

Everything Sidekick does is a **project**. The Cowork project folder is
the **root**. Everything lives underneath it.

```
<cowork-root>/                     ← the Cowork project folder = root
├── sidekick.settings.md           ← role + languages + connections (from init)
├── _triage/                       ← output of the scheduled scan (input for check-in)
│   └── YYYYMMDD-triage.md
├── projects/
│   ├── <project-slug>/
│   │   ├── CLAUDE.md              ← how Sidekick runs THIS project + brain index
│   │   ├── agenda.md              ← live items / planning per project
│   │   ├── brain/                 ← distilled, durable knowledge
│   │   ├── log/                   ← structured logbook (date + slug)
│   │   ├── archive/               ← processed source files (originals)
│   │   ├── output/                ← clean deliverables
│   │   └── data/                  ← structured data: one JSON file per table
│   │       ├── <table>.json       ←   a JSON array of row objects
│   │       └── _schema.json       ←   table → columns (+ types)
│   └── <another-project>/
│       └── …
└── _archive/
    └── projects/
        └── <archived-project>/    ← full project folder, moved here
```

### 3.0 Project scaffold

When a new project is created, Sidekick scaffolds the full structure:
`CLAUDE.md`, `agenda.md`, and the `brain/`, `log/`, `archive/`, `output/`
directories. `data/` is created lazily on the first structured data
(the first `create` makes `data/` and its first `<table>.json`).

### 3.1 Project detection (every session)

At the start of every substantive session, Sidekick first determines
**which project** is meant, before anything happens:

1. Read `projects/` and the `agenda.md` + brain index of existing
   projects.
2. Match the chat intent against existing projects.
3. **On a clear match:** briefly confirm which project is active and
   proceed.
4. **On no match or doubt:** put the choice to the user —
   *"Does this belong to project X, or shall I start a new project Y?"* —
   and do nothing until the user chooses.
5. **New project** → scaffold the full project structure (see 3.0).

Sidekick **never silently** creates a new project.

### 3.2 Project slug convention

`kebab-case`, short, descriptive: `core-roadmap`, `client-bpd`,
`q3-board-prep`. The slug is the folder name under `projects/`.

### 3.3 Archiving

Archiving a project = moving the entire project folder to
`_archive/projects/<slug>/`. Nothing is deleted. Archived projects no
longer participate in project detection, triage, or check-in, but remain
consultable. Handled by the `sidekick-archive` skill.

---

## 4. The structured-data layer (`data/`)

Structured project data lives in **plain JSON files** — one file per
"table" — under `projects/<slug>/data/`. Each `<table>.json` is a JSON
array of row objects (human-readable, git-diffable); `_schema.json` records
each table's columns and types. There is deliberately **no live database
file**: it was a binary blob the model could not inspect, and a stray
`DROP`/recreate wiped it. Plain files are inspectable, diffable, trivially
backed up, and there is no schema to drop.

**All access goes through one helper**, `scripts/data.py` (stdlib Python,
file-based). The model must **never** touch the data another way — not the
`sqlite3` CLI (absent in Cowork), not ad-hoc `python -c`, not a raw
read/edit of the JSON. Two reasons the helper is mandatory:

- **Reads** (`query`) run real SQL over a *throwaway in-memory SQLite*
  loaded from the files and discarded — full filter/sort/count power
  without pulling the whole file into context, and a read physically
  cannot touch the disk.
- **Writes** (`insert`/`update`/`delete`/`addcol`) are validated against
  the table's columns and **snapshot the file first** (a ring of the last
  20 under `data/.snapshots/`), so a mistaken edit is always recoverable.

Sidekick manages the store under three principles:

1. **Sidekick designs the tables itself.** When shared information is
   genuinely structured (lists, records, repeating fields), Sidekick
   decides which tables are needed.
2. **Extend over sprawl.** On new related information, Sidekick first
   uses `info` to check whether an existing table can take a column,
   before creating a new one. It must not become a tangle.
3. **Schema as knowledge.** The tables are documented in plain language in
   `brain/data-model.md`, so that Sidekick (and the user) can later
   easily write clear queries.

**Recognizing structured input — classify on arrival.** The routing
decision happens the moment input *arrives*, not only when Sidekick later
picks where to write. A shared spreadsheet, CSV, exported table, or any
tabular/repeating-record data is structured **by default**: the first
response is to **propose a table** (a structure change → confirm in plain
language), not to fold the rows into a log file or the brain. The brain
still receives the prose *insights* drawn from the data, the original file
goes to `archive/`, and the process is logged — but the rows themselves
live in `data/`. Folding a clearly tabular input straight into a log +
chat summary, with no table proposed, is the exact failure mode this layer
exists to prevent.

**Gatekeeper:** every structure change (new table, new column) is
presented to the user **non-technically**. Example: *"You're now also
sharing phone numbers with contacts. Shall I add those to the existing
contact list?"* — not: *"ALTER TABLE contacts ADD COLUMN phone TEXT."*

Reading data and **populating** existing tables with records that fit the
existing columns is free (no gatekeeper) — that is normal use, not a
structural change.

**Backups.** The structure is robust against accidents but not against
everything, so the **check-in makes a timestamped backup** of each
project's `data/` (`scripts/data.py backup`, written to `data/.backups/`)
before it processes anything. Per-write snapshots cover in-session slips;
the check-in backup is the durable, dated safety line.

See `references/data-discipline.md` for the full protocol.

---

## 5. The brain layer (`brain/`)

One brain per project, following the supplied method (see
`references/brain-protocol.md`, derived from "Setting up a project
brain"). Essence:

- **Distill, don't copy.** Key points to `brain/`, original to `archive/`.
- **Always show a diff**, write only after approval.
- **No new brain files without asking.**
- **Update existing lines** instead of stacking contradictory versions.
- The project's `CLAUDE.md` points to the brain files read at session
  start.

Input arrives through the chat — there is no separate inbox folder.

**Logs feed the brain too (the write-back safety net).** Besides writing
insights back to `brain/` inline during a session, durable insights captured in
`log/` are surfaced systematically: the **check-in** scans each project's `log/`
for files lacking the distilled stamp and folds them into the brain (with the
usual diff + approval), then stamps them. (The triage only reports an
undistilled-log count as a heads-up.) So a good discussion that landed in a log is
never lost, even if the inline write-back was missed. See §6, §10, §11.

---

## 6. The log layer (`log/`)

The log is the solution to Cowork's sprawl. Rules:

- Each chat gets a **start date + slug**: `20260301-research-financial.md`.
- Cowork logs **to disk, not to the chat** — in the chat only a short
  summary.
- Every time Sidekick wants to write something down, it **updates the
  existing log file** or writes a **new file** (again date + slug) if it
  concerns a different topic.
- This keeps the `log/` folder clear: one file per topic/session.

The log may be written freely — that is the whole point. No gatekeeper.

**Distilled-to-brain stamp.** When a log's durable insights have been captured
into `brain/` — which happens at the **check-in**, with approval — the check-in
appends a footer line to that log file:

```
> distilled to brain: 2026-06-01
```

The **check-in** finds the work: it scans each project's `log/` for files
**without** the stamp (except a log still being actively written), and distills
each into the brain (diff + approval), then writes the stamp. This closes the
loop `log → brain` without relying on remembering to write back inline. The
**triage** only reports an undistilled-log **count** per project as a heads-up —
it does not list or process them (so the same log can't pile up across triage
runs). Only the check-in writes the stamp (triage never writes outside
`_triage/`).

---

## 7. The output layer (`output/`)

Clean, explicitly requested deliverables: Word, Excel, PowerPoint, PDF,
etc. **Gatekeeper:** Sidekick asks for confirmation before every create,
edit, or delete in `output/`. Sidekick does not create documents here
unprompted. Output is generated in the **default output language** from
settings, unless the user explicitly requests another language.

---

## 8. The settings layer (`sidekick.settings.md`)

One file in the root, written by the `sidekick-init` skill. Contains:

- **Role** of the employee (free text; drives the advisor's tone/focus).
- **Chat language** — the language Sidekick communicates in with the user.
- **Default output language** — the language deliverables/output are
  generated in by default, unless explicitly requested otherwise.
- **Email connection** (yes / no).
- **Messages/chat connection** (no / Slack / Teams / Google Chat / other).
- **Storage connection** (no / Outlook / Google Drive / other).
- **Calendar connection** (no / Google Calendar / Outlook Calendar / other).

Chat language and output language are deliberately separate: a user may
chat in Dutch but want project documents in English.

Init asks these with multiple choice and creates **at least one project**,
so the structure is rolled out immediately. Init itself does **not** turn
connectors on — it only records what the user indicates, and afterwards
points the user to how the triage is scheduled and which connections may
need to be enabled for it.

---

## 9. Role adaptation

The role is captured at init. The always-on `sidekick` skill reads
`sidekick.settings.md` and tunes tone, focus, and the kind of advice to
that role. The baseline is role-description-driven (robust when rolled
out to others). Optional hook: if a role-specific skill is present in the
environment, Sidekick may use it — but the plugin functions fully without
it.

---

## 10. The triage layer (`sidekick-triage`, scheduled)

A single bundled skill that scans email + chat + calendar. Runs as a **scheduled
task** (frequency set by the user in Cowork, not in the plugin). Operation, at the
top level:

1. Review recent messages, emails, and calendar items (external sources).
2. **Note the undistilled-log count per project** (a heads-up only): how many
   `log/*.md` files lack the `> distilled to brain:` stamp. This is informational
   — a current snapshot, regenerated each run — **not** a per-log finding. The
   **check-in** is what actually detects and distills undistilled logs (§11), so
   the same log never piles up as a finding across multiple triage runs.
3. Write all findings to **`_triage/YYYYMMDD-HHMM-triage.md`** at the top level —
   a **timestamped file per run**, so triage can run **several times a day**
   without overwriting an earlier run.
4. **Never write to a project brain or log itself.** The `_triage/` files are
   purely **input for the check-in** that the user starts.

**Window (supports any cadence).** A run scans since the **run timestamp of the
most recent `_triage/*-triage.md` file** (not just the date), so a second run the
same day only covers what's new since the previous run. The first-ever run uses a
sensible default (e.g. last 7 days). Times are local to the workspace. The
check-in consumes **all** triage files written since the previous check-in
(deduping by source), so multiple runs per day are handled.

The human remains gatekeeper: triage does the heavy lifting (scanning and
proposing); the user decides via the check-in.

---

## 11. The check-in layer (`sidekick-checkin`, user-initiated)

The user starts the check-in themselves. Operation:

1. Walk through all (non-archived) projects.
2. Read each project's `agenda.md`.
3. Cross-reference it with the triage findings in `_triage/` and — if
   connected — the calendar.
4. **Scan the project's `log/` for undistilled logs** — files lacking the
   `> distilled to brain:` stamp (skip a log still being actively written).
   This is the check-in's own scan; it does not depend on the triage.
5. Propose concrete actions per project: update the brain, perform an
   action, create something in `output/`, reply to an email/chat, tick
   off an agenda item, **and distill each undistilled log into the brain.**
6. All proposed changes follow the normal gatekeeper rules (brain = diff
   + approval, output/db = confirmation).
7. **After distilling a log into the brain (on approval), stamp that log
   file** with `> distilled to brain: <date>`. If the user defers a log,
   leave it unstamped (it resurfaces at the next check-in).

The per-project `agenda.md` is deliberately simple (markdown): a list of
live items with status, so the check-in can work with it well.

---

## 12. Plugin structure (Cowork plugin)

Sidekick is built for **Claude Cowork only**. The structure follows the
standard Cowork plugin layout:

```
sidekick/
├── .claude-plugin/
│   ├── plugin.json                ← plugin manifest
│   └── marketplace.json           ← self-marketplace; lists this plugin, source "./"
├── skills/
│   ├── sidekick-core/             ← always-on main skill (NOT "sidekick" — see below)
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── interaction-style.md
│   │   │   ├── data-discipline.md
│   │   │   ├── brain-protocol.md
│   │   │   ├── write-disciplines.md
│   │   │   ├── project-claude-template.md
│   │   │   └── agenda-template.md
│   │   └── scripts/
│   │       └── data.py            ← file-based structured-data helper
│   ├── sidekick-init/
│   │   ├── SKILL.md
│   │   └── references/settings-template.md
│   ├── sidekick-triage/
│   │   ├── SKILL.md
│   │   └── references/triage-template.md
│   ├── sidekick-checkin/SKILL.md
│   └── sidekick-archive/SKILL.md
├── commands/                      ← flat files Cowork turns into typed /<name>
│   ├── sidekick-init.md           ← /sidekick-init → "Invoke the sidekick-init skill"
│   ├── sidekick-triage.md
│   ├── sidekick-checkin.md
│   └── sidekick-archive.md
├── docs/
│   └── ARCHITECTURE.md            ← this document
└── README.md
```

**Distribution.** Cowork installs *plugins* from *marketplaces*, so the repo
carries its own marketplace catalog at `.claude-plugin/marketplace.json`
listing one plugin named **`sidekick`** with `source: "./"` (the plugin root is
the repo root). Users add the repo as a marketplace, then install the `sidekick`
plugin from it.

**Typed commands come from `commands/`, not `skills/`.** In Cowork a
`skills/<name>/SKILL.md` is model-invocable and shows in the `/` menu, but the
**typed** `/<name>` command is produced by a flat `commands/<name>.md` file (a
thin wrapper whose body says *"Invoke the `<name>` skill"*). So each explicit
skill has a matching command file. This mirrors the working `solidcortex` plugin
(`commands/bootstrap-cortex.md` + `skills/bootstrap-cortex/`). The always-on
main skill (`sidekick-core`) has no command file — it fires by model-invocation.

**The real install-blocker was a malformed manifest, not the plugin name.** For
several iterations `/sidekick-init` returned *"Unknown command:
/sidekick:sidekick-init"* (and, after a rename, `/sidekick-cowork:sidekick-init`).
The cause: `plugin.json` had `repository` as an **object** (`{type, url}`), which
fails the manifest schema (it must be a **string**). Cowork loaded the skills
(filesystem discovery) but **rejected the commands** because the manifest was
invalid; the `<plugin>:<command>` text in the error was just Cowork's
command-not-found form. Verified locally: with the object `repository` the plugin
fails to install (`repository: expected string, received object`); with a string
it installs and all four `/sidekick-*` commands register. The always-on main
skill is named `sidekick-core` (kept distinct from the plugin name as a
precaution). The triage skill is also meant to be attached to a
Cowork **scheduled task**.

A plugin-wide interaction principle applies across all skills: when
putting a choice to the user, ask with **multiple choice** by default
(see `skills/sidekick-core/references/interaction-style.md`).

---

## 13. Build status (resolved during the plan units)

Resolved:

- **Init questionnaire** — finalized as seven multiple-choice questions
  mapped 1:1 to `sidekick.settings.md` (plan 03; field spec there).
- **`agenda.md` template** — finalized (plan 04), alongside the
  `project-claude-template.md` fix (brain read-line commented until the
  first brain file exists).
- **Connectors** — the **user** enables connectors in Cowork; the plugin
  only records intent and guides. There is **no `.mcp.json` auto-config**
  (superseded; the earlier open item is dropped).
- **Structured-data storage** — plain JSON files under `projects/<slug>/data/`
  (one `<table>.json` per table + `_schema.json`), all access through the
  stdlib helper `skills/sidekick-core/scripts/data.py`. Replaced the original
  single `data.sqlite` after testing (2026-06-01) showed the model bypassing
  the helper — it tried the absent `sqlite3` CLI, then ad-hoc `python -c`, and
  a stray recreate emptied the table. Files are inspectable + diffable, the
  helper snapshots before every write, queries run over a throwaway in-memory
  SQLite (no live DB to drop), and the check-in takes a dated backup.
- **Archive move primitive** — true rename/move, else copy → verify →
  remove; never delete before verified (plan 10).
- **Distribution as a marketplace** — Cowork adds *marketplaces*, not bare
  plugin repos. The repo ships `.claude-plugin/marketplace.json` (self-
  referencing, `source: "./"`) so it installs cleanly. Discovered during the
  first install attempt, 2026-06-01.

- **Command form — RESOLVED, root cause was the manifest (2026-06-01).** Two
  requirements: (1) **flat `commands/<name>.md` files** produce the typed
  `/<name>` command (skills/ alone only gives model-invocation + a menu entry),
  in the solidcortex format (`name:` frontmatter + "Invoke the `<name>` skill"
  body); (2) **`plugin.json` `repository` must be a string** — it was an object,
  which invalidated the manifest so Cowork rejected the commands. With both fixed
  (v0.2.6), the plugin is named `sidekick` and all four `/sidekick-*` commands
  register (verified by a local install). The earlier plugin-name churn
  (`solidbricks`, `sidekick-cowork`) was chasing a symptom; the name `sidekick`
  is fine once the manifest is valid. The main skill stays `sidekick-core`.

Remaining (verify-on-install):

- **Command resolution in Cowork** — after installing `sidekick` v0.2.6, confirm
  `/sidekick-init` (and the others) run when typed (`docs/MANUAL-TESTS.md` 0b).
