# Project structure — projects vs subprojects (areas)

Loaded on demand by the `sidekick` skill. Defines the **complete project
layout** (below) and the difference between a **top-level project** and a
**subproject / area**. Read this whenever the user talks about a "subproject",
"sub-area", or work "under"/"within"/"part of" an existing project — or when you
are unsure where a file belongs.

## The complete project layout (every file has a home)

A project is `projects/<slug>/`. **Only two files sit loose in the project
root** — `CLAUDE.md` and `agenda.md`. Everything else lives in a dedicated
folder. **Nothing else lands in the root, ever.** If you're about to write
something with no obvious home, it belongs in `log/`.

```
projects/<slug>/
├── CLAUDE.md     ← project memory, read at session start          [root file]
├── agenda.md     ← the running agenda / to-dos                    [root file]
├── brain/        ← distilled, durable knowledge (gated: diff + approval)
├── data/         ← structured data store: JSON tables via data.py (lazy)
├── dashboard/    ← dashboard definitions: <slug>-dashboard.sk.json (queries, not numbers)
├── artifacts/    ← generated dashboard HTML (synced to Drive)
├── output/       ← ONLY approved, final deliverables (synced) — keep clean
├── log/          ← working area: dated activity logs + in-progress drafts (free)
├── archive/      ← superseded originals (e.g. a distilled source file)
└── .sidekick/    ← internal machine state: reports.json (recipe registry) +
                    sync.json (sync manifest). Hidden; never synced; you don't
                    hand-edit it (the save_report tool + sync engine own it).
```

Created **eagerly** at scaffold: `CLAUDE.md`, `agenda.md`, `brain/`, `log/`,
`archive/`, `output/`, plus `dashboard/` + `artifacts/` (the empty dashboard
skeleton). Created **lazily** on first use: `data/` (first table), `.sidekick/`
(first registry/sync write).

**Where each kind of work goes — so nothing lands in the root:**
- **Structured / tabular data** → `data/`, only via `data.py` (never a loose JSON).
- **Knowledge worth keeping** → `brain/` (distilled, gated).
- **A deliverable you're still working on** (a draft doc, deck, sheet, text) →
  `log/` — it's work-in-progress, written freely. **It moves to `output/` only
  when the user approves it as final** (and then it syncs). That keeps `output/`
  clean: finished work only.
- **Scratch / intermediate files** (a temp export, a file mid-conversion) →
  `log/`. Never the project root.
- **An original you imported and distilled** (the source spreadsheet/email) →
  `archive/`.
- **A dashboard** → its definition in `dashboard/`, its built HTML in
  `artifacts/` (built by the `build_dashboard` tool).
- **Recipe registry / sync manifest** → `.sidekick/` (written by the
  `save_report` tool and the sync engine — not by hand).

Data **backups/snapshots** stay inside `data/` (`.snapshots/`, `.backups/`).
The system folders `_triage/` and `_archive/` live at the **Cowork workspace
root**, not inside a project — don't confuse `_archive/` with a project's
`archive/`.

## The two levels

Sidekick has a **flat** project structure: every project lives directly under
`projects/<slug>/` with the layout above (`CLAUDE.md` + `agenda.md` in the root;
`brain/ data/ dashboard/ artifacts/ output/ log/ archive/ .sidekick/` folders).
The cross-project skills (triage, check-in, status, find, archive) all run over
these **top-level** projects.

A **subproject is not a second project.** It is an **area within a parent
project's harness** — a looser separation for a strand of work that is big
enough to keep apart but still clearly belongs to the parent.

| | **Top-level project** | **Subproject / area** |
|---|---|---|
| Where | `projects/<slug>/` | inside an existing `projects/<parent>/` |
| Own `CLAUDE.md` | yes | **no** (parent's) |
| Own `agenda.md` | yes | **no** (parent's, optional heading) |
| Knowledge | `brain/` | `brain/<sub>/` (subfolder) |
| Deliverables | `output/` | `output/<sub>/` (subfolder) |
| Logs / archive | own `log/`, `archive/` | parent's (slug may name the area) |
| Scaffold | full scaffold | **none** — just the two subfolders |
| Seen by triage/checkin/status/find | as a project | **as part of the parent** |

**The cardinal rule:** a subproject **never** becomes a nested
`projects/<parent>/<sub>/`, and **never** gets its own `CLAUDE.md` or
`agenda.md`. Nesting a project breaks detection, triage, check-in, and status
(they only walk the direct children of `projects/`) — which is exactly why a
nested project is wrong. An area, living inside the parent's `brain/` and
`output/` and the parent's `agenda.md`, is covered automatically.

## How to choose — and when to ask

- **New top-level project** — a distinct body of work with its own agenda and
  lifecycle: its own client, mandate, product, or initiative. It would have
  its own running to-do list.
- **Subproject / area** — a strand *within* such a body of work that shares
  the parent's agenda, context, and people. Signals: the user says "under",
  "within", "part of", "a sub-area of <existing project>", or the work would
  share the parent's agenda.

**When it is unclear, ask** — via the interactive picker — *"A new project, or
an area inside <parent>?"* Never silently turn an area into a nested project,
and never silently fold a genuinely separate project into another as an area.

## Creating a subproject (area)

Once the parent is known and the user has confirmed it's an **area** (not a
new project):

1. **Knowledge folder.** Create `projects/<parent>/brain/<sub>/` and seed
   `projects/<parent>/brain/<sub>/overview.md` — a short statement of what the
   area is and its current status. This is a brain write: **show the diff of
   `overview.md` and write after approval** (per `brain-protocol.md`). The
   area may later grow per-topic files/subfolders under `brain/<sub>/`.
2. **Deliverables folder.** Create `projects/<parent>/output/<sub>/` for the
   area's deliverables (it may stay empty until the first deliverable; create
   it now so the area's home is clear). Deliverables inside it still follow
   the output gatekeeper (confirm before create/edit/delete).
3. **Agenda.** Put the area's agenda items in the **parent's** `agenda.md`,
   optionally under a `## <sub>` heading. Do **not** create a separate agenda.
4. **Parent `CLAUDE.md`.** Add `brain/<sub>/overview.md` to the parent's
   "Read at session start" list, and add a one-line note describing the
   subproject as an area of this project.
5. **Log** the creation in the parent's `log/` as usual (free).

**Do not** create `projects/<parent>/<sub>/`, a `<sub>/CLAUDE.md`, a
`<sub>/agenda.md`, or any other project scaffold for the area.

### Worked example

> "Add a subproject *competitor-scan* under *market-strategy*."

Produces:

```
projects/market-strategy/
├── CLAUDE.md                         ← "Read at session start" now lists
│                                       brain/competitor-scan/overview.md;
│                                       a note names the area
├── agenda.md                         ← items added under "## competitor-scan"
├── brain/
│   └── competitor-scan/
│       └── overview.md               ← what the area is (approved)
└── output/
    └── competitor-scan/              ← deliverables for the area
```

It does **not** create `projects/market-strategy/competitor-scan/CLAUDE.md`
or any nested project.

## Detection guard (read alongside the SKILL's project detection)

- **Only the direct children of `projects/` are projects.** When listing or
  detecting projects, never descend into a project's subfolders looking for
  more projects — `brain/<area>/` and `output/<area>/` are areas, not
  projects.
- On a clear "area within <parent>" intent, run the steps above. On a clear
  "new, separate body of work" intent, scaffold a top-level project. On doubt,
  ask via the picker.

## Promoting or splitting later

If an area outgrows the parent and needs its own agenda and lifecycle, it can
be **promoted** to a top-level project (move `brain/<sub>/` → a new
`projects/<sub>/brain/`, set up a scaffold, lift its agenda items across).
Treat that as a deliberate, confirmed move — not the default. The default for
a strand of work is an area inside the parent.
