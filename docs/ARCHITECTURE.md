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
│   │   ├── brain/                 ← distilled, durable knowledge (areas: brain/<sub>/)
│   │   ├── log/                   ← structured logbook (date + slug)
│   │   ├── archive/               ← processed source files (originals)
│   │   ├── output/                ← clean deliverables (areas: output/<sub>/)
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

Scaffolding applies **only to top-level projects** (direct children of
`projects/`). A **subproject** — an area *within* a project (§3.4) — is
**never** scaffolded: it adds only a `brain/<sub>/` and an `output/<sub>/`
subfolder inside its parent and reuses the parent's `agenda.md` and
`CLAUDE.md`. It gets no `CLAUDE.md`, no `agenda.md`, and never a nested
`projects/<parent>/<sub>/`.

### 3.1 Project detection (every session)

At the start of every substantive session, Sidekick first determines
**which project** is meant, before anything happens:

1. Read `projects/` and the `agenda.md` + brain index of existing
   projects. **Only the direct children of `projects/` are projects** — a
   folder nested inside a project is never a standalone project (nested work
   is a subproject/area, §3.4).
2. Match the chat intent against existing projects.
3. **On a clear match:** briefly confirm which project is active and
   proceed.
4. **On no match or doubt:** put the choice to the user —
   *"Does this belong to project X, or shall I start a new project Y?"* —
   and do nothing until the user chooses.
5. **New project** → scaffold the full project structure (see 3.0).
6. **Subproject / area intent** → when the user clearly means a strand
   *within* an existing project ("a subproject of X", "an area under X",
   "part of X"), route to the **subproject flow** (§3.4) — do **not** create
   a new or nested project. When it is unclear whether something is a new
   project or an area inside one, **ask** (via the picker).

Sidekick **never silently** creates a new project, and **never silently
turns an area into a nested project** (or a new project into an area).

### 3.2 Project slug convention

`kebab-case`, short, descriptive: `core-roadmap`, `client-bpd`,
`q3-board-prep`. The slug is the folder name under `projects/`.

### 3.3 Archiving

Archiving a project = moving the entire project folder to
`_archive/projects/<slug>/`. Nothing is deleted. Archived projects no
longer participate in project detection, triage, or check-in, but remain
consultable. Handled by the `sidekick-archive` skill.

### 3.4 Subprojects (areas within a project)

A **subproject is not a project.** It is a named **area within an existing
project's harness** — a looser separation than a top-level project, for a
strand of work big enough to keep apart but still clearly belonging to the
parent. It gets **no own `CLAUDE.md`, no own `agenda.md`, no separate
scaffold, and never a nested `projects/<parent>/<sub>/`.** It reuses the
parent's harness:

- **Knowledge** → `projects/<parent>/brain/<subproject>/` — a brain
  subfolder, which may itself hold per-topic files/subfolders. Its anchor is
  `brain/<subproject>/overview.md` (what the area is).
- **Deliverables** → `projects/<parent>/output/<subproject>/`.
- **Agenda** → items live in the parent's existing `agenda.md` (optionally
  under a `## <subproject>` heading). There is **no** separate agenda.
- **Logs / archive** stay shared at the parent level (a log slug may name the
  area, e.g. `20260602-<subproject>-research.md`).
- The **parent `CLAUDE.md`** describes the subproject as an area and adds
  `brain/<subproject>/overview.md` to its "Read at session start" list.

Because everything lives inside the parent, the subproject is **automatically
covered** by project detection, triage, check-in, status, and find — it is
never enumerated as a separate project and never falls outside the loop (the
exact failure of a nested project).

**Project vs subproject — how to choose.** A **new top-level project** is a
distinct body of work with its own agenda and lifecycle (its own client,
mandate, product). A **subproject/area** is a strand *within* such a body of
work that shares the parent's agenda, context, and people. Signals for an
area: the user says "under", "within", "part of", "a sub-area of <existing
project>", or the work would share the parent's agenda. **When in doubt,
ask** — via the picker — "a new project, or an area inside <parent>?"

**Example.** "Add a subproject *competitor-scan* under *market-strategy*"
produces `projects/market-strategy/brain/competitor-scan/overview.md` and
`projects/market-strategy/output/competitor-scan/`, puts its agenda items
under a heading in `projects/market-strategy/agenda.md`, and adds the
overview to `projects/market-strategy/CLAUDE.md`. It does **not** create
`projects/market-strategy/competitor-scan/CLAUDE.md` or any nested project.

See `references/project-structure.md` for the full protocol.

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
  cannot touch the disk. **Answering any question about the data goes
  through `query`** — never a raw read/`grep` of the JSON. `info` reports
  the distinct values of low-cardinality columns, so a filter matches the
  real spelling (`ON-PREM`, not `ONPREM`) instead of guessing.
- **Writes** (`insert`/`update`/`delete`/`addcol`) are validated against
  the table's columns and **snapshot the file first** (a ring of the last
  20 under `data/.snapshots/`); snapshotting is best-effort, so a sandbox
  that blocks it never aborts the write. A whole sheet inserts in one call
  (`--json` takes an array).

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

## 7b. The presentation & reporting layer (`sidekick-report`)

Once a project has a `data/` store, the natural next want is to **surface**
it: answer the same question repeatedly without re-deriving it, and present
the data in a form a human can actually read (a dashboard, a sheet). This
layer turns the structured store into reusable views. It owns **no new
storage discipline** — it reuses the brain and output gatekeepers — and it
**never** reaches the data any way but through `scripts/data.py query`.

**A report is a recipe plus a rendered artifact.** The two halves live in
the two layers that already exist:

| Half | Where | Gatekeeper | What it is |
|------|-------|------------|------------|
| **Recipe** (the reusable "software") | `brain/reports.md` | diff + approval | a named, plain-language report: its purpose + the `SELECT`(s) it runs (+ the render kind) |
| **Rendered artifact** (the deliverable) | `output/` | confirm | the produced file: an `.html` dashboard, a sheet, a markdown table |

So the two cases this layer exists for:

1. **Reusable software for a recurring ask.** "Give me the monthly revenue
   breakdown again" should not mean re-deriving a query each time. Sidekick
   saves the report as a **recipe** in `brain/reports.md` (a name, a plain
   description, and the exact `SELECT`). Re-running it = look up the recipe,
   run `data.py query`, format the result. The recipe *is* the reusable
   software; the brain is its home because it is durable project knowledge.

2. **A live, interactive artifact (tabbed dashboard).** Sidekick produces a
   **single self-contained `output/<name>.html`** with client-side tabs,
   sorting, filtering, and charts. Each tab is fed by one of the recipe's
   queries.

**The data flow — discipline-preserving.** The model **always** sources the
data with `data.py query` and **bakes the result into the artifact as a
snapshot** (embedded JSON). It never makes the artifact read a raw
`data/*.json` file, and it never hand-reads the JSON to fill the page — the
single-access-path rule from §4 holds here too. "Live" therefore means
**interactive over a snapshot**: the tabs/sorting/charts run in the page,
but the numbers are as of the moment it was generated. **Refresh = re-run
the report**, which re-queries and rewrites the artifact.

The dashboard HTML is **dumb** — the agent generates it from the recipe with
the **computed rows baked in**; the calculation rule stays in the recipe, never
in the page. It lives in the project's **`artifacts/`** folder.

**Built from the Sidekick UI kit.** The page is not hand-rolled — every
dashboard/list/grid artifact starts from one shared design system (the
Solidbricks/Visma look: collapsible sidebar, centered workspace title, tabbed
views, light/paper/dark toggle, KPI & section cards, bar / horizontal-bar
charts, sortable grids, list+detail; brand orange `#F47800` + blue `#1493E8`,
Ubuntu/Open Sans/JetBrains type stacks; the real Solidbricks logo in the footer).
The kit ships as assets — `assets/ui.css` + `ui.js` + `solidbricks.png` — that a
build script, **`scripts/dashboard.py`**, reads from disk and bakes into the
page. The agent **never reads or pastes the kernel** (an inline paste made Cowork
truncate *the read* at ~11 KB → blank pages, v0.14.0); it only edits a small
per-project **`artifacts/<slug>-dashboard.sk.json`** — the `window.SK` data
(collections → views, each `kind: dashboard | grid | listdetail | home`), built
from query results. Each active project has **one** dashboard, "<Project>
Dashboard", created as an empty skeleton at scaffold time; adding content edits
the `.sk.json` and rebuilds in place. The kit is self-contained (no network), so
the built file is both the snapshot and the body the live artifact loads. Full
guide + data model: `references/ui-kit.md`. The user can restyle freely.

**Live Cowork artifact (the primary deliverable).** In Cowork the dashboard the
user sees is a **live artifact**, not a file handed over with `present_files`.
The artifact sandbox blocks **local files and local MCP servers** (a local
`sidekick-data` server was tried and removed) — only **cloud connectors** are
reachable. So the live artifact is a **thin wrapper**, created **once** with
`mcp__cowork__create_artifact`, that loads the dashboard html from Drive via the
**Drive connector** (`download_file_content`, base64 → iframe `srcdoc`); it is the
only artifact that calls a connector.

- The built `artifacts/<slug>-dashboard.html` is **synced to Drive** (the sync
  covers `artifacts/` as well as `output/`, §7c).
- On a data/rule change the agent **edits the `.sk.json`, re-runs
  `dashboard.py build`, and re-syncs**, overwriting the **same Drive file in
  place** (stable file id) — **no new artifact, no approval**. Cowork's refresh
  re-pulls it.
- Without Drive/sync, fall back to presenting the built `.html` as a one-off
  **snapshot** (opens anywhere, no auto-update) — the same file, shown directly.
- The recipe is registered in `projects/<slug>/.reports.json` (project root,
  never scanned as a table) via `scripts/reports.py` — recording its `sql`,
  the `artifact` path, the `tables` it reads (so a change knows what to
  regenerate, `reports.py uses`), and the synced HTML's `drive_file_id`.

Rules live in the recipe in **both** modes; the page only renders. Live
requires the Drive connector (the wrapper reads it) and Output sync on (the HTML
reaches Drive); otherwise fall back to a plain snapshot.

**Gatekeepers, reused as-is:**

- Saving or changing a **recipe** is a brain write → **diff + approval**
  (and it is documented in plain language, like any brain entry).
- Producing or overwriting the **dashboard HTML** in `artifacts/` →
  **confirmation**, like any deliverable, in the default output language. The
  **wrapper** is emitted once; later refreshes overwrite the Drive HTML, not the
  artifact.
- Reading the data to build either → **free** (it is a `query`).

The `sidekick-report` skill drives this (typed `/sidekick-report`, and the
core skill routes a clear "show me / dashboard this / report on the data"
intent here). It is **not** read-only — it writes a recipe (gated) and an
artifact (gated) — but it adds no new gatekeeper of its own.

---

## 7c. Optional: output sync to external storage

By default `output/` lives only in the Cowork workspace. When the user sets an
**Output sync base path** (§8) — a folder on a mounted/synced storage drive
(Google Drive for Desktop, OneDrive, …) reachable from the workspace —
Sidekick keeps each project's `output/` **and `artifacts/`** (generated
dashboard HTML, §7b) **in step both ways** with that storage: finished work
lands where the user (and colleagues) keep files, edits made *there* flow back
in, and a live dashboard's HTML reaches Drive so its wrapper can read it. Only
those two folders are synced; brain, log, data, and the gatekeepers are
untouched.

**A native MCP server does the sync — not the model, not a connector, not a
sandboxed shell.** All file movement goes through the bundled **`sidekick-sync`
MCP server** (`scripts/sync_server.py`, stdlib Python, declared in
`.claude-plugin/plugin.json` under `mcpServers`), which does plain
**binary-safe file copies** between the local `output/` and the base path. Its
engine is shared with the `scripts/sync.py` CLI (same functions); the CLI
remains for environments with a native shell and for local testing. Three hard
reasons for this shape, all found in testing:

- **No bytes through the model.** Sending a file through a storage *connector*
  made the model **base64-encode it into its own output** (~size×1.33 tokens,
  emitted token-by-token) — an Excel push that ran past five minutes. A file
  copy costs **zero model tokens**.
- **The copy must reach the watched filesystem.** Writing from the **bash
  sandbox** to a Linux mountpoint did **not** trigger the storage client's
  sync (confirmed: a shell `reconcile` reported success but the file never
  appeared in Drive).
- **A plugin MCP server runs as a native host process** — so its copies land
  on the real filesystem the storage client watches (e.g. `G:\My Drive\…`) and
  sync fires. The model calls its tools (`reconcile_output`, `resolve_output`)
  with **paths only**.

**Layout — base path, then one folder per project.** Under the base path each
project gets `<slug>/output/`, mirroring its workspace `output/` tree (area
subfolders included). There is **no** `sidekick-` prefix — the base path the
user chose is itself the Sidekick root, so settings records only the path, not
per-project names.

```
<base path>/                    e.g. G:\My Drive\sidekick
├── <project-a>/output/         ↔ projects/<project-a>/output/
└── <project-b>/output/         ↔ projects/<project-b>/output/
```

**When it syncs.** The model calls the **`reconcile_output`** tool (`project:
projects/<slug>`, `base: <path>`) at three moments: **after a confirmed output
write** (the new/edited file copies out), and **at session start for the
active project** and **as a sweep at the check-in** (§11) — each reconcile
pulls external edits in and pushes local ones out.

**The reconcile rule (per file).** A small **manifest**
`projects/<slug>/.sidekick-sync.json` (path → last-synced content hash; at the
*project* root, **not inside `output/`**, so it is never itself synced) holds
the baseline. For every file across local ∪ external ∪ manifest:

| Situation | Action |
|---|---|
| Same content both sides | in sync |
| **One** side changed vs the baseline | copy the changed side over the other |
| **Both** changed vs the baseline (or no baseline, contents differ) — a **conflict** | left untouched, **reported** — the model asks the user (below), never overwrites silently |
| File on **one** side only | copied to the other (**additive**) |
| Gone on **both** sides | dropped from the manifest |

After reconciling, the manifest is rewritten. On the **first** sync (no
manifest) every file counts as new and is copied across — no false conflicts.

**Conflicts go to the human.** Reconcile never resolves a conflict itself. On a
reported conflict the model asks the user via the **picker** — keep the Cowork
version, keep the external version, or keep both — then calls **`resolve_output`**
(`file`, `keep` ∈ `local|external|both`; `both` keeps the local file and the
external one as `<name>.from-external<ext>` on both sides).

**Additive — sync never deletes.** A file on only one side is copied to the
other, so a delete is **not** propagated; to fully remove a deliverable, delete
it on **both** sides. This favours never losing data in a shared drive (the
trade: a one-sided delete is re-created from the surviving side).

**Gatekeepers — none added.** The deliverable was already confirmed under the
output gatekeeper (§7); pushing it out is a mechanical consequence of sync
being on. A routine pull (an external edit the user made deliberately) applies
without a prompt — the *setting* is the standing consent — **except** a true
conflict, the one moment Sidekick stops to ask.

**When it runs, and failure handling.** Sync runs only when Output sync is on
**and** a base path is set and reachable; with no base path it simply does not
run — there is **no connector fallback for files** (the connector route is the
slow/broken one this design replaces). If the base path is unreachable or a
copy fails, the tool reports it (`errors` in its result) and the model tells
the user what didn't sync and continues — sync never blocks a local write or
deletes data. The next session-start / check-in reconcile retries. The
remaining deploy dependency: the host must be able to launch the MCP server
(**Python on PATH**; otherwise set an absolute interpreter in the manifest
`command`) — verify once (§13). If the `sidekick-sync` tools are unavailable,
the model falls back to the `sync.py` CLI and warns that a sandboxed copy may
not reach the storage client. Full protocol: `references/sync-discipline.md`.

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
- **Output sync** (no / yes) — turn two-way `output/` sync on (§7c). Recorded
  as a plain **yes/no**; per-project folders are derived at runtime, never
  written here.
- **Output sync base path** (blank / a folder path) — the storage folder sync
  copies to/from, e.g. `G:\My Drive\sidekick`. Should be a **mounted/synced
  Drive or OneDrive folder** reachable from the workspace; under it Sidekick
  keeps `<slug>/output/` per project (§7c). **Blank ⇒ sync does not run** —
  there is no connector fallback for files. Only relevant when Output sync is
  yes.
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
8. **Reconcile output sync — both directions** (only if Output sync is on and
   a base path is set, §7c): per project, call the **`reconcile_output`** tool
   (`project: projects/<slug>`, `base: <path>`) — it pulls external edits in and
   pushes local ones out (**additive**, never deletes). For each path in its
   `conflicts`, **ask the user** via the picker and call **`resolve_output`**. A
   failed step / unreachable base path is reported, not fatal.

The per-project `agenda.md` is deliberately simple (markdown): a list of
live items with status, so the check-in can work with it well.

---

## 11b. The read-only layer: status & recall

Triage scans *inbound*, the check-in drives *actions*. Two **read-only**
skills round out the loop — they never write anything, so they carry no
gatekeeper and can run anytime.

### `sidekick-status` (user-initiated) — "where does everything stand?"

A quick, read-only glance across all non-archived projects. For each it
reports, without proposing anything:

- open `agenda.md` items and anything marked waiting-on;
- the count of **undistilled logs** (files in `log/` lacking the
  `> distilled to brain:` stamp);
- the date of the last check-in (from `log/YYYYMMDD-checkin.md`);
- the `data/` tables and their row counts (via `data.py info`);
- staleness (no activity in a while) and, if a calendar is connected,
  upcoming items in the near term.

Output is a **short prose summary**, not proposal cards — it decides
nothing, so there are no pickers; it may end by suggesting the user run
`/sidekick-checkin` if action is due. It is the read-only sibling of the
check-in.

### `sidekick-find` (user-initiated + model-invoked) — cross-project recall

Answers "where did we decide X?" / "which project mentions Y?" across
**all** projects at once — the recall the per-project session-start read
can't give. It searches each project's `brain/`, `log/`, and `agenda.md`
(markdown, grep-able) and, for `data/`, uses `data.py info`/`query` to spot
tables/columns/values that match. The core skill routes a clear recall
question here even without the explicit command.

It returns a **prose list of hits** (project → file → snippet, original
language preserved). It writes nothing; if the user then wants to act on a
hit, it offers — through the interactive picker — to open that project and
hands off to the normal flow. Read-only, so no backup or gatekeeper needed.

---

## 12. Plugin structure (Cowork plugin)

Sidekick is built for **Claude Cowork only**. The structure follows the
standard Cowork plugin layout:

```
sidekick/
├── .claude-plugin/
│   ├── plugin.json                ← plugin manifest (+ `mcpServers`: sidekick-sync)
│   └── marketplace.json           ← self-marketplace; lists this plugin, source "./"
├── skills/
│   ├── sidekick-core/             ← always-on main skill (NOT "sidekick" — see below)
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── interaction-style.md
│   │   │   ├── data-discipline.md
│   │   │   ├── brain-protocol.md
│   │   │   ├── write-disciplines.md
│   │   │   ├── project-structure.md
│   │   │   ├── reporting.md
│   │   │   ├── ui-kit.md          ← design system + window.SK data model for artifacts
│   │   │   ├── sync-discipline.md
│   │   │   ├── project-claude-template.md
│   │   │   └── agenda-template.md
│   │   ├── assets/                ← baked into dashboards by dashboard.py (agent never pastes them)
│   │   │   ├── ui.css             ← Solidbricks design tokens + component CSS (3 themes)
│   │   │   ├── ui.js              ← render kernel: shell + dashboard/grid/listdetail/home
│   │   │   └── solidbricks.png    ← real maker logo (footer; base64-embedded at build)
│   │   └── scripts/
│   │       ├── data.py            ← file-based structured-data helper (+ query() function)
│   │       ├── dashboard.py       ← builds <slug>-dashboard.html from <slug>-dashboard.sk.json + the kit
│   │       ├── reports.py         ← report-recipe registry + CLI (.reports.json; runs via data.query)
│   │       ├── sync.py            ← sync engine + CLI (output/ + artifacts/ ↔ external base path)
│   │       └── sync_server.py     ← `sidekick-sync` MCP server (native; wraps sync.py)
│   ├── sidekick-init/
│   │   ├── SKILL.md
│   │   └── references/settings-template.md
│   ├── sidekick-triage/
│   │   ├── SKILL.md
│   │   └── references/triage-template.md
│   ├── sidekick-checkin/SKILL.md
│   ├── sidekick-archive/SKILL.md
│   ├── sidekick-status/SKILL.md   ← read-only cross-project overview
│   ├── sidekick-find/SKILL.md     ← read-only cross-project recall/search
│   └── sidekick-report/SKILL.md   ← saved reports + dashboards over data/ (via data.py)
├── commands/                      ← flat files Cowork turns into typed /<name>
│   ├── sidekick-init.md           ← /sidekick-init → "Invoke the sidekick-init skill"
│   ├── sidekick-triage.md
│   ├── sidekick-checkin.md
│   ├── sidekick-archive.md
│   ├── sidekick-status.md
│   ├── sidekick-find.md
│   └── sidekick-report.md
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

- **Init questionnaire** — seven multiple-choice questions mapped 1:1 to
  `sidekick.settings.md` (plan 03; field spec there), plus a **conditional
  output-sync question (6b)** asked only when a storage connection is chosen
  (added 2026-06-02 with §7c; recorded as Output sync: No when storage is no).
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
  **Keep `data.py` small.** Cowork truncates the helper on install past a hard
  threshold — measured precisely 2026-06-02: a 15915-byte copy was cut at byte
  **15808** (mid-`def main(`), breaking it and forcing the model back to raw
  JSON. The earlier "lean" rewrite (~15800 B) sat only ~8 B under the cliff, so
  a tiny +115 B edit re-broke it. Now trimmed to **14962 B (~846 B margin)** and
  the docstring carries a `BUDGET: keep under 15 KB` banner. Keep prose in
  `data-discipline.md`, not the script (no large docstrings/help/examples). A
  truncated install surfaces as a `SyntaxError`/"'(' was never closed" — skills
  are told to treat that as truncation, not fall back to raw JSON.
- **Archive move primitive** — true rename/move, else copy → verify →
  remove; never delete before verified (plan 10).
- **Read-only layer (added 2026-06-01, post-test)** — `sidekick-status`
  (cross-project overview) and `sidekick-find` (cross-project recall/search),
  see §11b. Both are read-only (no writes, no gatekeeper, no `data.py` change),
  report in prose, and reuse existing reads + `data.py info`/`query`. They round
  out the loop alongside triage (inbound) and the check-in (actions).
- **Subprojects / areas (added 2026-06-02)** — a subproject is **not** a
  nested project; it is an area inside a parent (§3.4): knowledge in
  `parent/brain/<sub>/`, deliverables in `parent/output/<sub>/`, agenda items
  in the parent's `agenda.md`, and the parent `CLAUDE.md` lists
  `brain/<sub>/overview.md`. **No** `parent/<sub>/CLAUDE.md`, no separate
  scaffold, never a nested `projects/<parent>/<sub>/`. Only direct children of
  `projects/` count as projects, so triage/check-in/status/find cover the area
  as part of the parent without counting it separately. Protocol in
  `references/project-structure.md`; the always-on skill and `sidekick-init`
  both enforce the project-vs-area split.
- **Presentation & reporting layer (added 2026-06-02)** — `sidekick-report`
  (§7b) surfaces the `data/` store: a **recipe** (named report = purpose +
  `SELECT`(s)) saved in `brain/reports.md` (diff + approval) and a **rendered
  artifact** in `output/` (confirm) — a self-contained, tabbed `.html`
  dashboard with the queried rows **embedded as a snapshot**. Data is always
  sourced via `data.py query` (never a raw JSON read, never an artifact reading
  the table); refresh = re-run the report. No new gatekeeper (reuses brain +
  output); `data.py` is **unchanged** (keeps the ~16 KB install cap). A richer
  React render was deferred — it would depend on Cowork's still-new live-artifact
  runtime, which the self-contained-HTML snapshot does not.
- **Output sync to external storage (added 2026-06-02; iterated to a native
  MCP server same day, v0.7.0 → v0.10.0)** — optional **two-way** sync of each
  project's `output/` with an external storage folder (§7c, §8). Final design:
  a bundled **`sidekick-sync` MCP server** (`scripts/sync_server.py`, stdlib
  stdio, declared in `plugin.json` `mcpServers`) does plain **binary-safe file
  copies** between `projects/<slug>/output/` and `<base path>/<slug>/output/`;
  it shares its engine with the `scripts/sync.py` CLI. The model calls
  **`reconcile_output`** after a confirmed write and at session start /
  check-in, and **`resolve_output`** for conflicts — **paths only**, never
  bytes. A manifest `projects/<slug>/.sidekick-sync.json` (path → content
  **hash**; project root, not synced) detects one-sided changes vs **conflicts**
  (both-changed → the model **asks** via the picker; keep Cowork / external /
  both). **Additive** — a delete is never propagated (to remove, delete both
  sides). Settings: **Output sync** (yes/no) + **Output sync base path** (a
  mounted/synced folder, e.g. `G:\My Drive\sidekick`); **no base path ⇒ no
  sync**. The iteration, all the same session per user testing:
  - **v0.7.0** one-way mirror; **v0.8.0** two-way + settings stores only yes/no
    (first cut wrongly wrote the per-project postfix into the file); **v0.8.1**
    flagged the transport problem; **v0.9.0** replaced the connector with a CLI;
    **v0.10.0** moved the transport to a native MCP server after the CLI failed
    in Cowork; **v0.10.1** fixed the path resolution (CONFIRMED syncing to Drive
    in Cowork).
  - **Why the MCP server.** Three real failures: (1) connector upload made the
    model **base64 the binary into its own output** (~size×1.33 tokens) — an
    Excel push past five minutes; (2) a CLI copy from the **bash sandbox**
    reported success but the file **never reached Drive** (sandbox writes to a
    Linux mountpoint the Drive client doesn't watch); (3) fix — a **plugin MCP
    server runs as a native host process**, so its copies land on the watched
    filesystem and sync fires. **Confirmed working in Cowork (v0.10.1):** files
    pushed to `G:\My Drive\sidekick\<slug>\output\` and appeared in Drive.
  - **The path-resolution fix (v0.10.1).** In Cowork the server's
    `CLAUDE_PROJECT_DIR` points to a scratchpad (AppData), **not** the workspace
    (`C:\Claude Cowork\Sidekick`), so a **relative** `project` resolved to an
    empty dir and the tool silently synced nothing. Fix: the tools now take the
    **absolute** project path (the skills pass `<workspace root>/projects/<slug>`,
    where the root is the dir holding `sidekick.settings.md`), and `reconcile`
    returns a **`warnings`** entry when the local output dir is missing so a
    wrong path is loud, not silent.
  - **Deploy dependency:** the host launches the server with **Python on PATH**
    — if the `sidekick-sync` tools don't appear, set an absolute interpreter in
    the manifest `command`; the model falls back to the CLI with a warning.
    `references/sync-discipline.md` has the one-time Drive-appears test.
- **Live (MCP-backed) reporting — `sidekick-data` server (added 2026-06-02,
  v0.11.0)** — a second, **read-only** plugin MCP server lets a **live artifact
  fetch a saved recipe's output by name** so calculation rules live in the
  recipe (the agent owns + verifies them), never in the artifact's JS. Pieces:
  a recipe **registry** `projects/<slug>/.reports.json` managed by
  `scripts/reports.py` (mirrors the gated `brain/reports.md`); `data.py`'s query
  refactored into a reusable **`query()` function** (no new subcommand; trimmed
  back under the ~16 KB cap); the `sidekick-data` server (`reports_server.py`)
  exposing **`run_report`** / **`list_reports`** (read-only, executes via
  `query()` — SQL over all tables, multi-table JOINs included). The artifact
  passes only the **name** + an **absolute** project path, parses the MCP
  content array, and **always embeds a snapshot fallback** for when no server is
  present. Snapshot stays the default; live is opt-in. Decision rationale
  (this session): Excel-as-store was considered and **rejected** — it re-creates
  the SQLite failure (binary blob, dependency, and openpyxl writes formulas it
  can't evaluate, so the agent can't verify computed values); JSON stays the
  record, calc rules live as SQL recipes the agent runs, Excel only as an
  optional human-facing export.
- **Live reporting reworked to Drive-wrapped — `sidekick-data` server removed
  (2026-06-02, v0.12.0).** Testing settled the bridge question: the **artifact
  sandbox blocks local files, localhost, and local plugin MCP servers** — only
  **cloud connectors** (Drive) are reachable, and **every `update_artifact` is
  approval-gated**. So the `sidekick-data` server (run_report over a local MCP)
  was **deleted** — useless to artifacts. The live model is now **Drive-wrapped**
  (§7b): the agent generates a self-contained dashboard HTML into the project's
  new **`artifacts/`** folder (data baked in, rules in the recipe), **syncs it to
  Drive** (`sync.py` extended to sync `artifacts/` alongside `output/`), and a
  **thin wrapper artifact** — emitted once — loads the Drive HTML via the Drive
  connector (`download_file_content` → base64 → iframe). Refresh without
  approval = regenerate the HTML + re-sync (overwrites the same Drive file in
  place); the wrapper re-pulls on Cowork's own refresh. `.reports.json` now also
  stores each recipe's `artifact` path, `tables`, and `drive_file_id`
  (`reports.py uses` finds dashboards to regenerate on a data change). `reports.py`
  + the registry stay; only the MCP server is gone. **Confirmed working in
  Cowork** (Y-variant: artifact wrapping a Drive HTML re-loads un-gated). Two
  env-specific values the agent resolves at setup: the Drive download tool name
  (`mcp__<uuid>__download_file_content`, per-install) and the synced HTML's Drive
  file id (stable across overwrites).
- **Shared design system — the Sidekick UI kit (2026-06-03, v0.13.0).** Every
  generated artifact now starts from one **Solidbricks/Visma design system**
  instead of a hand-rolled page: a collapsible sidebar, centered workspace title,
  tabbed views, light/paper/dark toggle, and a widget set (KPI & section cards,
  bar / horizontal-bar charts, sortable grids, status pills, list+detail), in the
  brand palette (orange `#F47800` + blue `#1493E8`). Derived from a reference app
  the user supplied (`plan/Sidekick (offline).html`, a React/Babel bundle) and
  **ported to dependency-free vanilla JS** — the wrapped iframe can reach no
  network, so React/Babel/Google-Fonts CDNs are out; the demo's hardcoded views
  were generalized into a **declarative `window.SK`-driven renderer** (smaller
  *and* reusable). It ships as **two raw assets** the agent pastes in full —
  `skills/sidekick-core/assets/ui.css` + `ui.js` (split because Cowork truncates
  any single installed file past ~15.8 KB; the written artifact in `artifacts/`
  has no cap). View kinds: `dashboard | grid | listdetail | home`, plus an
  `empty` placeholder. Data still comes only from `data.py query`; computed rows
  baked in; calc in the recipe. New reference `references/ui-kit.md` (data model +
  assembly skeleton); `reporting.md`'s old inline skeleton replaced by a pointer
  to it. A combined runnable preview lives at `plan/sidekick-ui-base.html`
  (dev-only, never read at runtime). The user can restyle freely — it is a
  starting point, not a cage.
- **Truncation bug found & guarded (2026-06-03, v0.13.1).** First Cowork run of
  the kit failed at every step: the model built its own Chart.js dashboard in
  `output/`, hand-read `data/*.json`, wrote its own wrapper, saved no recipe —
  it never invoked `sidekick-report`. Root cause was **not** weak prompting: the
  always-on `sidekick-core/SKILL.md` had grown to **19144 B**, and Cowork
  truncates an installed file at ~**15808 B**, so the entire "Presenting the
  data" routing rule plus three later sections sat **past the cut and were
  silently dropped** — the model literally never received the instruction. Fix:
  added an imperative **"Showing data → ALWAYS the `sidekick-report` skill"**
  hard rule (the six failure modes enumerated as forbidden) placed **early**
  (byte ~8.5 K, well inside the kept region), and **trimmed the whole file to
  15123 B** (deferring detail to the references it already cites). New validator
  **Check 7** fails the build if any runtime-loaded file under `skills/` (SKILL,
  references, scripts, assets) exceeds the cap, so this class of silent
  truncation can't recur (`data.py` hit the same cliff at 0.3.3/0.11.1). The fix
  is plugin-side, so it reaches every install + every project on reinstall — no
  per-workspace `CLAUDE.md`/settings band-aid needed.
- **Dashboards: build script + per-project + live-artifact-primary (2026-06-03,
  v0.14.0).** A second Cowork run surfaced three issues. (a) **Agent-read
  truncation:** the agent had to read+paste the ~11 KB `ui.js` to assemble a
  dashboard, and Cowork truncated *the read* at ~11.4 KB (`E(SK.workspa…`) →
  blank pages. The shipped `ui.js` was complete on disk; the failure was the
  inline paste, not install truncation. (b) The hand-built footer used a
  hand-drawn SVG instead of the **real Solidbricks logo**. (c) The skill pointed
  at a `.html` file + `present_files` rather than the **live Cowork artifact**
  that is the actual deliverable. Fixes: a new **`dashboard.py`** reads
  `ui.css`+`ui.js`+`solidbricks.png` from disk (native, full — no context limit)
  and bakes the complete page, so **the agent never reads or pastes the kernel**;
  it only edits a tiny per-project **`artifacts/<slug>-dashboard.sk.json`** (the
  `window.SK` data). The real 256-px logo is base64-embedded (in the generated
  html, which has no cap) and exposed as `window.SB_LOGO`; the sidebar name is
  hard-coded "Sidekick" (header = workspace, footer = "by Solidbricks"). Each
  **active project gets one dashboard**, "<Project> Dashboard", built as an empty
  skeleton at scaffold time; "add X to the dashboard" edits the `.sk.json` and
  rebuilds in place — a **new** artifact only on explicit request. The **live
  Cowork artifact** (`mcp__cowork__create_artifact` wrapping the Drive html) is
  the primary deliverable, not the file. reporting.md / ui-kit.md / core + report
  SKILLs rewritten accordingly; validator tracks the two new files.
- **Distribution as a marketplace** — Cowork adds *marketplaces*, not bare
  plugin repos. The repo ships `.claude-plugin/marketplace.json` (self-
  referencing, `source: "./"`) so it installs cleanly. Discovered during the
  first install attempt, 2026-06-01.

- **Locating bundled scripts — `$CLAUDE_PLUGIN_ROOT` is NOT in the shell
  (2026-06-02).** The harness expands `${CLAUDE_PLUGIN_ROOT}` only inside
  `plugin.json` (the two `mcpServers` args) and hook commands — **never** in a
  Bash call the model runs, where it is empty. So every skill instruction of the
  form `python3 "$CLAUDE_PLUGIN_ROOT/.../data.py" …` resolved to a bare
  `/skills/...` path and failed; the documented fallback
  `~/.claude/plugins/sidekick/...` was also wrong (real install lives under a
  hashed `cache/<owner>/<plugin>/<hash>/`). **Fix:** skills resolve the scripts
  dir by search —
  `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`
  — then call `"$SK/data.py"` / `reports.py` / `sync.py`. This is the same `find`
  the tester used by hand, proven to work inside the Cowork sandbox. The MCP
  route (sync/data servers) is unaffected — those launch from `plugin.json` with
  the correct root. Canonical snippet: `data-discipline.md` → Locating the
  helper. (Future direction: fold the CLI ops behind MCP tools so no path
  resolution is needed at all, as sync/reports already did.)

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
