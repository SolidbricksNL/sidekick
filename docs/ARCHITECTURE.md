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
| 3b | **Database** (structure) | `data.sqlite` | **Ask for confirmation** on schema change | **non-technical** |

The reasoning: the log is allowed to fill up freely, because that is
exactly where work-in-progress belongs instead of in the chat. The brain
and the output are precious and durable, so the human stands as
gatekeeper there. The database structure is technically sensitive, so
schema changes are always presented **in plain language** — never as SQL
or technical jargon.

**Rule of thumb for Sidekick itself:** "Before I write anything, I ask
myself: is this log (free), brain (diff + approval), or output/db
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
│   │   └── data.sqlite            ← structured data + schema knowledge
│   └── <another-project>/
│       └── …
└── _archive/
    └── projects/
        └── <archived-project>/    ← full project folder, moved here
```

### 3.0 Project scaffold

When a new project is created, Sidekick scaffolds the full structure:
`CLAUDE.md`, `agenda.md`, and the `brain/`, `log/`, `archive/`, `output/`
directories. `data.sqlite` is created lazily on first structured data.

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

## 4. The database layer (`data.sqlite`)

One SQLite file per project. Sidekick manages it autonomously, under
three principles:

1. **Sidekick designs the tables itself.** When shared information is
   genuinely structured (lists, records, repeating fields), Sidekick
   decides which tables are needed.
2. **Extend over sprawl.** On new related information, Sidekick first
   investigates whether an existing table can be extended, before
   creating a new one. It must not become a tangle.
3. **Schema as knowledge.** The schema is documented in plain language in
   `brain/data-model.md`, so that Sidekick (and the user) can later
   easily write clear queries.

**Gatekeeper:** every schema change (new table, new column, removed
column) is presented to the user **non-technically**. Example: *"You're
now also sharing phone numbers with contacts. Shall I add those to the
existing contact list?"* — not: *"ALTER TABLE contacts ADD COLUMN phone
TEXT."*

Reading data and **populating** existing tables with records that fit the
existing schema is free (no gatekeeper) — that is normal use, not a
structural change.

See `references/database-discipline.md` for the full protocol.

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

A single bundled skill that scans email + chat + calendar. Runs as a
**scheduled task** (frequency set by the user in Cowork, not in the
plugin). Operation, at the top level:

1. Review recent messages, emails, and calendar items.
2. Write the findings to `_triage/YYYYMMDD-triage.md` at the top level.
3. **Never write to a project brain itself.** The `_triage/` file is
   purely **input for the check-in** that the user starts.

The human remains gatekeeper: triage does the heavy lifting (scanning and
proposing); the user decides via the check-in.

---

## 11. The check-in layer (`sidekick-checkin`, user-initiated)

The user starts the check-in themselves. Operation:

1. Walk through all (non-archived) projects.
2. Read each project's `agenda.md`.
3. Cross-reference it with the triage findings in `_triage/` and — if
   connected — the calendar.
4. Propose concrete actions per project: update the brain, perform an
   action, create something in `output/`, reply to an email/chat, tick
   off an agenda item.
5. All proposed changes follow the normal gatekeeper rules (brain = diff
   + approval, output/db = confirmation).

The per-project `agenda.md` is deliberately simple (markdown): a list of
live items with status, so the check-in can work with it well.

---

## 12. Plugin structure (Cowork plugin)

Sidekick is built for **Claude Cowork only**. The structure follows the
standard Cowork plugin layout:

```
sidekick/
├── .claude-plugin/
│   └── plugin.json                ← manifest (only this inside .claude-plugin/)
├── skills/
│   ├── sidekick/                  ← always-on main skill
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── interaction-style.md
│   │       ├── database-discipline.md
│   │       ├── brain-protocol.md
│   │       ├── write-disciplines.md
│   │       ├── project-claude-template.md
│   │       └── agenda-template.md
│   ├── sidekick-init/
│   │   ├── SKILL.md
│   │   └── references/settings-template.md
│   ├── sidekick-triage/
│   │   ├── SKILL.md
│   │   └── references/triage-template.md
│   ├── sidekick-checkin/SKILL.md
│   └── sidekick-archive/SKILL.md
├── docs/
│   └── ARCHITECTURE.md            ← this document
└── README.md
```

Skills invoke each other via slash commands (e.g. `/sidekick-init`,
`/sidekick-checkin`). The main skill `sidekick` fires automatically when
relevant; the others are explicit actions. The triage skill is intended
to be attached to a Cowork **scheduled task**.

A plugin-wide interaction principle applies across all skills: when
putting a choice to the user, ask with **multiple choice** by default
(see `skills/sidekick/references/interaction-style.md`).

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
- **SQLite execution** — via the bundled stdlib helper
  `skills/sidekick/scripts/db.py`, not the `sqlite3` CLI (plan 06).
- **Archive move primitive** — true rename/move, else copy → verify →
  remove; never delete before verified (plan 10).

Remaining (verify-on-install):

- **Command form in Cowork** — whether the explicit skills appear as
  `/sidekick:<skill>` (namespaced), `/<skill>` (bare), or not as `/`
  commands at all. Settled by the install check in `docs/MANUAL-TESTS.md`
  (step 0b); fallback is thin `commands/<skill>.md` wrappers. Command
  references are left in the bare form until this is observed.
