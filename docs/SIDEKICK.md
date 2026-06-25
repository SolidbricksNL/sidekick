# Sidekick — Complete Guide

> A plain-language handbook for Sidekick: what it is, what it does, how to
> use it, the problems it solves, and the background behind its design.
> For the engineering source of truth, see
> [`ARCHITECTURE.md`](./ARCHITECTURE.md) — every skill is derived from it.

---

## Table of contents

1. [What is Sidekick?](#1-what-is-sidekick)
2. [What does it do?](#2-what-does-it-do)
3. [What problems does it solve?](#3-what-problems-does-it-solve)
4. [The core idea: projects + three write disciplines](#4-the-core-idea-projects--three-write-disciplines)
5. [The skills, one by one](#5-the-skills-one-by-one)
6. [How to use it](#6-how-to-use-it)
7. [A day in the life](#7-a-day-in-the-life-worked-example)
8. [Data, reports & dashboards](#8-data-reports--dashboards)
9. [Output sync to Drive / OneDrive](#9-output-sync-to-drive--onedrive)
10. [Settings & languages](#10-settings--languages)
11. [Background & design history](#11-background--design-history)
12. [Limitations & things to know](#12-limitations--things-to-know)
13. [Glossary](#13-glossary)

---

## 1. What is Sidekick?

**Sidekick is a personal-advisor plugin for [Claude Cowork](https://www.anthropic.com).**
It turns Cowork from a blank chat window into a structured, opinionated work
environment that behaves like a personal assistant tuned to *your* role.

Three things define it:

- **Role-adaptive.** At setup you describe your role — Managing Director,
  client consultant, marketer, analyst, anyone. Sidekick reads that and tunes
  its tone, focus, and the kind of advice it gives. The same plugin serves an
  entire company; each person gets an advisor shaped to their job.
- **Discipline-enforcing.** Sidekick never just "writes something somewhere."
  Every piece of information it produces is classified and routed into one of a
  few well-defined homes, each with its own rule about whether you need to
  approve it. This is the heart of the plugin (see §4).
- **Cowork-only by design.** Sidekick is built for Claude Cowork and nothing
  else. It installs at the user level (so it technically loads everywhere), but
  a built-in **surface gate** keeps it silent and inert in Claude Code, the
  desktop chat, or any code repo — it only "wakes up" inside a real Sidekick
  workspace in Cowork (see §12).

In one sentence: **Sidekick gives every employee a tidy, rule-governed
workspace so that knowledge, deliverables, and data stop getting lost in the
chat.**

---

## 2. What does it do?

Concretely, Sidekick:

- **Organises all work into flat "projects."** Each project is a self-contained
  folder with a fixed, predictable structure. Nothing floats loose.
- **Keeps a clean process log** of every working session on disk (not in the
  chat), so the chat stays short and nothing is lost when the conversation is
  compacted.
- **Maintains a "brain"** per project — a distilled, durable memory of the
  important decisions and facts — and updates it only with your approval.
- **Produces deliverables** (Word, Excel, PowerPoint, PDF, HTML) into a clean
  `output/` folder, always asking for confirmation first.
- **Manages structured data** (lists, records, tables) in plain JSON files you
  can query with real SQL, without ever needing a database.
- **Builds live dashboards** from that data — branded, interactive HTML
  dashboards that refresh when the data changes.
- **Scans your inbound world** — email, chat (Slack/Teams/Google Chat), and
  calendar — on a schedule, and reports what needs attention.
- **Drives an action loop** ("check-in") that walks every project, cross-checks
  it against what the scan found, and proposes concrete next steps.
- **Recalls across projects** ("where did we decide X?") and gives a read-only
  status overview of everything at once.
- **Syncs deliverables** two-way with a shared Google Drive / OneDrive folder so
  colleagues see finished work where they already keep files.
- **Archives** finished projects without ever deleting anything.
- **Onboards new users** with an interactive guided tour.

All of this is delivered as **nine Markdown skills** plus one small native
**MCP server** (`sidekick-sync`) that handles file copying and dashboard builds.

---

## 3. What problems does it solve?

Sidekick exists to fix **Cowork's two sprawl failure modes**:

### Problem 1 — Everything ends up in the chat

By default, Claude does its thinking, research, and note-taking *in the
conversation*. That feels fine until:

- the chat gets long and slow,
- the conversation is **compacted** (summarised to save space) and detail is
  silently lost,
- you can never find "that thing we worked out three chats ago."

**Sidekick's fix:** work is logged **to disk** in a per-project `log/` folder,
with only a short summary left in the chat. The log is allowed to fill up
freely — that's exactly where work-in-progress belongs. The chat stays light.

### Problem 2 — Scattered, unstructured documents

The opposite habit is just as bad: a new untitled document on every chat, no
naming convention, no findability, duplicated and contradictory notes.

**Sidekick's fix:** every write has **exactly one correct home** and a rule
about who approves it (the three write disciplines, §4). Durable knowledge is
distilled into the `brain/`; deliverables go to `output/`; repeating records go
to `data/` as proper tables. Nothing lands loose.

### The deeper problem — no enforcement

Earlier versions discovered that *telling* the model to be tidy isn't enough —
a skill only runs when the model decides to invoke it, and Cowork doesn't fire
plugin hooks. So Sidekick anchors its hard rules in a **workspace `CLAUDE.md`**
that Cowork auto-loads every single session (and re-injects after compaction).
That file is the always-on contract: *read settings, route every write into a
project, never write loose to the workspace root.* This is what makes the
discipline actually stick (see §11).

---

## 4. The core idea: projects + three write disciplines

### Everything is a project

The Cowork project folder is the **workspace root**. Underneath it, every body
of work is a **project** — a flat, direct child of `projects/`. The structure
is fixed and predictable:

```
<workspace-root>/                  ← the Cowork project folder
├── CLAUDE.md                      ← always-on contract (auto-loaded every session)
├── sidekick.settings.md          ← your role + languages + connections
├── _triage/                      ← scheduled-scan output (input for the check-in)
├── projects/
│   └── <project-slug>/
│       ├── CLAUDE.md             ← how Sidekick runs THIS project + brain index
│       ├── agenda.md             ← live items / planning for this project
│       ├── brain/                ← distilled, durable knowledge        (diff + approval)
│       ├── log/                  ← process logbook (date + slug)       (write freely)
│       ├── output/               ← clean deliverables                  (confirm)
│       ├── data/                 ← structured data: one JSON file per table
│       ├── dashboard/            ← editable dashboard definitions (local)
│       ├── artifacts/            ← built dashboard HTML (synced to Drive)
│       ├── archive/              ← processed source files (originals)
│       └── .sidekick/            ← hidden machine state (recipe registry, sync manifest)
└── _archive/projects/           ← archived projects (moved here, never deleted)
```

**Subprojects (areas).** A strand of work *within* a project is **not** a nested
project — it's an *area*. It lives in `brain/<area>/` and `output/<area>/`,
shares the parent's `agenda.md`, and is automatically covered by every loop
(triage, check-in, status, find). This avoids the trap of a nested project that
falls outside the loops.

### The three write disciplines

This is the heart of Sidekick. **Everything it writes falls into exactly one
category, each with its own gatekeeper rule:**

| Category | Where | Gatekeeper | Why |
|---|---|---|---|
| **Log** (process) | `log/` | **Write freely** — no permission | Work-in-progress belongs on disk, not in chat |
| **Brain** (memory) | `brain/` | **Show a diff + get approval** | Durable knowledge is precious; you stay the gatekeeper |
| **Output** (deliverables) | `output/` | **Ask for confirmation** | Deliverables are final; never created unprompted |
| **Structured data** (structure) | `data/` | **Confirm in plain language** | Adding a table/column is a structural change; records that fit existing columns flow in freely |

The rule Sidekick applies to itself before any write: *"Is this log (free),
brain (diff + approval), or output/data (confirmation)?"*

A crucial nuance: **structure changes are always explained in plain language**,
never as SQL. You'll hear *"You're now also sharing phone numbers with your
contacts — shall I add those to the contact list?"*, never
*"ALTER TABLE contacts ADD COLUMN phone."*

---

## 5. The skills, one by one

Sidekick ships **nine skills**. One is always-on; the rest are triggered by a
typed `/command` (and some can also be invoked automatically when your intent is
clear).

| Skill | How it fires | What it does |
|---|---|---|
| **Sidekick Core** | Automatic, on any work | The backbone: detects which project you mean, enforces the three write disciplines, self-heals the workspace contract, runs session startup. Never named directly. |
| **Sidekick Init** | `/sidekick-init` | One-time setup wizard. Multiple-choice questions for role, languages, and connections; writes `sidekick.settings.md` + the workspace `CLAUDE.md`; scaffolds your first project. |
| **Sidekick Guide** | `/sidekick-guide` | Interactive onboarding tour. Pure conversation — explains the core principle and every skill, group by group. Runs *before* setup; reads nothing but settings; writes nothing. |
| **Sidekick Triage** | Scheduled / `/sidekick-triage` | Read-only scan of email + chat + calendar. Writes findings to `_triage/`. Never touches a project's brain or log — it only produces input for the check-in. |
| **Sidekick Check-in** | `/sidekick-checkin` | The action loop. Walks every project, cross-references triage + calendar, distills undistilled logs into the brain, and proposes concrete actions — all under the normal gatekeepers. |
| **Sidekick Status** | `/sidekick-status` | Read-only overview. Where every project stands: open agenda items, undistilled-log counts, last check-in, data table row counts, staleness. Proposes nothing. |
| **Sidekick Find** | `/sidekick-find` | Read-only cross-project recall. "Where did we decide X?" searches every project's brain, log, agenda, and data at once. |
| **Sidekick Report** | `/sidekick-report` | Turns a project's `data/` store into saved reports (recipes) and branded, interactive HTML dashboards. |
| **Sidekick Archive** | `/sidekick-archive` | Retires a project by moving its whole folder to `_archive/`. Never deletes. |

**A note on the loop.** Triage scans *inbound* → the check-in drives *actions*
→ status and find are *read-only* lenses on the whole set. Together they form a
closed loop: nothing inbound is missed, nothing gets lost, and you can always
ask "where does everything stand?" without changing anything.

---

## 6. How to use it

### First-time setup

1. **Install the plugin in Cowork** (see [§ Distribution](#how-it-is-distributed)
   below). Cowork installs *plugins* from *marketplaces*, so you add the
   Sidekick repo as a marketplace, then install the `sidekick` plugin from it.
2. **Run `/sidekick-guide`** for an interactive tour of the principle and every
   skill. It's pure conversation and runs even before setup — start here if
   you're new.
3. **Run `/sidekick-init`** (or just say *"set up my Sidekick workspace"*). A
   short multiple-choice setup captures your role, chat language, default output
   language, and which connections you want. It writes your settings, the
   workspace contract, and scaffolds your first project. It does **not** turn
   any connector on.
4. **Enable connectors** you said yes to (email / messages / storage / calendar)
   in **Cowork's own connector settings**. The plugin only records *intent*; you
   enable the actual connections.
5. **Schedule triage (optional).** Attach `sidekick-triage` to a Cowork
   **scheduled task** and pick a frequency (e.g. daily). The plugin doesn't set
   the frequency — Cowork does.

### Everyday use

- **Just start working.** Describe what you're doing; Sidekick figures out which
  project it belongs to (or asks), and keeps everything structured automatically.
- **`/sidekick-checkin`** — review across all projects and act on what triage
  found.
- **`/sidekick-status`** — a quick read-only "where does everything stand?".
- **`/sidekick-find`** — recall something across projects.
- **`/sidekick-report`** — turn a project's data into a dashboard.
- **`/sidekick-archive`** — retire a finished project.
- **`/sidekick-guide`** — a refresher on what each skill does, anytime.

### How it talks to you

A plugin-wide rule: when Sidekick puts a choice to you, it asks with
**multiple choice** by default — tapping beats typing in Cowork. Open questions
are reserved for genuinely free-form answers (a project name, a reply body).

---

## 7. A day in the life (worked example)

> You're a sales lead. A colleague shares a spreadsheet of deals in chat.

1. **Project detection.** Sidekick checks which project this belongs to. No
   clear match → it asks: *"New project, or part of an existing one?"* You pick
   "new project: Q3-pipeline." It scaffolds `projects/q3-pipeline/`.
2. **Structured input recognised.** The spreadsheet is tabular, so Sidekick
   proposes a table in plain language: *"Shall I keep these deals as a table
   with columns product, platform, ARR, stage?"* You confirm — the rows land in
   `data/deals.json`, the original file goes to `archive/`, and the *insights*
   (not the raw rows) are distilled into the `brain/`.
3. **A dashboard.** You say *"show me this."* `/sidekick-report` builds a branded
   dashboard (`artifacts/q3-pipeline-dashboard.html`) with KPIs and charts bound
   to live queries. It's saved as a reusable recipe.
4. **A deliverable.** You ask for a board-ready summary. Sidekick confirms,
   then writes `output/q3-pipeline-summary.docx`.
5. **Triage (overnight).** The scheduled scan notices two emails about a deal and
   a calendar item, and writes them to `_triage/`.
6. **Check-in (next morning).** `/sidekick-checkin` cross-references the agenda
   with the triage findings, proposes replying to the emails and updating the
   ARR on one deal, distills yesterday's log into the brain, and rebuilds the
   dashboard with the new number — each step gated appropriately.
7. **Recall (next week).** *"What did we decide about the on-prem deal?"* →
   `/sidekick-find` surfaces the brain entry across all projects.

---

## 8. Data, reports & dashboards

### Structured data without a database

Structured project data lives in **plain JSON files** — one per "table" — under
`data/`, with a `_schema.json` recording columns and types. There is
deliberately **no database file**: a binary blob the model couldn't inspect, and
a stray `DROP` once wiped it. Plain files are inspectable, diffable, trivially
backed up, and there's no schema to drop.

All access goes through one bundled helper, `data.py`:

- **Reads** run real SQL over a *throwaway in-memory copy* of the files —
  full filter/sort/count/JOIN power, and a read physically can't touch the disk.
- **Writes** are validated against the table's columns and **snapshot the file
  first** (a rolling backup). The check-in also takes a dated backup of each
  project's `data/`.

Sidekick designs the tables itself, prefers extending an existing table over
creating new ones, and documents the schema in plain language in
`brain/data-model.md`.

### Reports = recipe + rendered artifact

A **report** has two halves, each living in a layer that already exists:

- **The recipe** (the reusable "software"): a named, plain-language report — its
  purpose plus the exact `SELECT`(s) it runs — saved in the brain (diff +
  approval). Re-running a recurring ask means looking up the recipe, not
  re-deriving a query.
- **The rendered artifact** (the deliverable): a single self-contained,
  interactive HTML dashboard in `output/` / `artifacts/` (confirm).

### Dashboards

Every dashboard is built from the **Sidekick UI kit** — a shared Solidbricks/
Visma design system (collapsible sidebar, tabbed views, light/paper/dark toggle,
KPI & section cards, charts, sortable grids, list+detail; brand orange `#F47800`
+ blue `#1493E8`). You never hand-roll a page.

The key design point: the dashboard definition (`dashboard/<slug>-dashboard.sk.json`)
stores **query bindings, not hardcoded numbers**. Each KPI/chart/table carries a
`query` or `recipe`; the build resolves them against the *live* data and bakes in
fresh rows. So a data change just means **rebuild** — no hand-editing, no
desync. After any data write, Sidekick proactively rebuilds the dashboard in the
same turn.

---

## 9. Output sync to Drive / OneDrive

By default `output/` lives only in the Cowork workspace. Turn on **Output sync**
(in settings) and set a **base path** to a mounted/synced Drive or OneDrive
folder, and Sidekick keeps each project's `output/` **and `artifacts/`** in step
**both ways** with that storage:

- Finished work lands where you (and colleagues) already keep files.
- Edits made *there* flow back in.
- A live dashboard's HTML reaches Drive so it can render in Cowork.

The sync is handled by a **native MCP server** (`sidekick-sync`), not the model —
for three reasons found in testing: routing bytes through the model base64-encoded
files into its own output (a 5-minute hang); a sandbox shell copy never reached
the Drive client; and a native host process *does* land copies on the watched
filesystem. The model only passes **paths**, never bytes.

Sync is **additive** (a delete is never propagated — to remove a file, delete it
on both sides) and **conflict-safe** (if both sides changed, Sidekick asks which
version wins rather than overwriting). No base path ⇒ sync simply stays idle;
there is no fallback that routes files through the chat.

---

## 10. Settings & languages

`sidekick.settings.md` (written by `/sidekick-init`) records:

- **Role** — free text; drives the advisor's tone and focus.
- **Chat language** — how Sidekick talks to you.
- **Default output language** — the language of deliverables.
- **Connections** — email (yes/no), messages (Slack/Teams/Google Chat/…),
  storage, calendar.
- **Output sync** (yes/no) + **base path**.

Chat language and output language are deliberately separate: you might chat in
Dutch but want documents in English.

---

## 11. Background & design history

Sidekick was built and hardened **entirely through real Cowork testing**, and
several of its most important design choices are scar tissue from things that
broke. The short version:

- **Why a database became plain JSON files.** The original `data.sqlite` was a
  binary blob the model couldn't inspect; it bypassed the helper, tried the
  absent `sqlite3` CLI, then ad-hoc Python, and a stray recreate emptied a table.
  Plain JSON files + a mandatory helper (queries over a throwaway in-memory copy,
  snapshots before writes) fixed it for good.
- **Why the rules live in a workspace `CLAUDE.md`.** The discipline first rested
  on the always-on `sidekick-core` skill — but a skill only fires when the model
  invokes it, and **Cowork ignores plugin hooks** (no SessionStart/PreToolUse).
  The one always-on layer Cowork honours is a `CLAUDE.md` in the workspace root,
  auto-loaded every session and re-injected after compaction. So the hard rules
  moved there, and `sidekick-core` self-heals the file if it's missing.
- **The ~15,808-byte truncation cliff.** Cowork silently truncates any installed
  skill file past ~15.8 KB. This once dropped the tail of `sidekick-core/SKILL.md`
  (so the model literally never received the "always use the report skill" rule)
  and broke `data.py` mid-function. The fixes: critical rules are placed *early*
  in each file, large content is split into references and <9 KB chunks, and a
  **structure validator (Check 7) + CI + pre-commit hook** now fail the build if
  any runtime file exceeds the cap.
- **Why sync and dashboard builds run in a native MCP server.** The sandbox
  shell can't reach the Drive client, and the plugin mount truncates large
  bash-reads of plugin scripts. A native host process avoids both — so file
  copies, dashboard builds, and the recipe registry all run through the
  `sidekick-sync` server, not bash.
- **Why dashboards bind to live queries.** Early dashboards stored hardcoded
  numbers, so a data change meant the model hand-edited every KPI — error-prone
  and instantly out of sync. Now the definition stores *bindings*, and a rebuild
  bakes fresh rows.
- **The surface gate (v1.0.0).** Because the plugin installs user-level, it
  loaded into Claude Code and plain chats too and tried to apply workspace rules
  there. The gate makes Sidekick stand down silently anywhere that isn't a real
  Sidekick workspace in Cowork.

The single source of truth for all of this — and the full, dated change log — is
[`ARCHITECTURE.md`](./ARCHITECTURE.md). If you change the design, change that
document first, then the skills.

---

## 12. Limitations & things to know

- **Cowork only.** Sidekick is built for Claude Cowork. It does nothing useful
  in Claude Code or the desktop chat — the surface gate keeps it inert there.
  (Residual cost: the skill *descriptions* and the MCP server still *load*
  everywhere; the gate stops *behaviour*, not loading. You can hard-disable per
  code repo via `.claude/settings.json` → `"enabledPlugins"`.)
- **Connectors are yours to enable.** The plugin records which connections you
  want but never turns them on — you do that in Cowork's settings.
- **Triage frequency is set in Cowork**, not the plugin (via a scheduled task).
- **Output sync needs a real mounted folder** (Drive for Desktop / OneDrive) and
  **Python on the host PATH** for the MCP server. No base path ⇒ no sync.
- **Keep skill files under ~15.8 KB.** If you contribute, run
  `node scripts/validate-structure.mjs` before committing — CI and the
  pre-commit hook enforce it.
- **Sync is additive** — it never deletes across sides; remove a file on both
  sides to fully delete it.

---

## 13. Glossary

| Term | Meaning |
|---|---|
| **Workspace root** | The Cowork project folder; holds `CLAUDE.md`, `sidekick.settings.md`, `projects/`, `_triage/`, `_archive/`. |
| **Project** | A flat, self-contained body of work under `projects/<slug>/`. Direct children of `projects/` only. |
| **Subproject / area** | A strand *within* a project — lives in the parent's `brain/<area>/` + `output/<area>/`, never a nested project. |
| **Write discipline** | The rule deciding where a write goes and who approves it: log (free), brain (diff + approval), output/data (confirm). |
| **Brain** | A project's distilled, durable knowledge. Updated only with approval. |
| **Log** | A project's process logbook on disk. Written freely; the antidote to chat sprawl. |
| **Output** | Clean, explicitly requested deliverables. Confirmed before every write. |
| **Triage** | The scheduled read-only scan of email/chat/calendar → `_triage/`. |
| **Check-in** | The user-initiated action loop that proposes next steps across all projects. |
| **Recipe** | A named, reusable report (purpose + its SQL) saved in the brain. |
| **Surface gate** | The mechanism that keeps Sidekick silent outside a Cowork Sidekick workspace. |
| **`sidekick-sync`** | The bundled native MCP server that does file copies and dashboard builds. |

---

*Sidekick is a Solidbricks plugin for Claude Cowork. Current version: **1.0.0**.*
