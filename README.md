# Sidekick

A generic, role-adaptive personal advisor plugin for **Claude Cowork**.
It gives any employee — Managing Director, client consultant, marketer,
anyone — a structured, discipline-enforcing work environment.

Sidekick exists to fix Cowork's two failure modes: dumping everything
into the chat (lost at compaction) and creating scattered, unstructured
working documents. It does this by anchoring all work in **projects** and
enforcing three **write disciplines**.

## The idea in one picture

```
<cowork-root>/
├── sidekick.settings.md      # role, languages, connections
├── _triage/                  # scheduled scan output → input for check-in
├── projects/
│   └── <slug>/
│       ├── CLAUDE.md         # how Sidekick runs this project
│       ├── agenda.md         # live items
│       ├── brain/            # distilled memory   (diff + approval)
│       ├── log/              # process logbook     (free)
│       ├── archive/          # processed originals
│       ├── output/           # deliverables        (confirmation)
│       └── data/             # structured data: JSON tables via data.py
└── _archive/projects/        # archived projects (moved, never deleted)
```

Projects are flat: each is a direct child of `projects/`. A strand of work
*within* a project is a **subproject/area**, not a nested project — it lives in
the parent's `brain/<area>/` and `output/<area>/` and shares the parent's
`agenda.md`, so triage, check-in, status, and find cover it automatically.

## The three write disciplines

| What | Where | Gatekeeper |
|---|---|---|
| Process, work-in-progress | `log/` | Write freely |
| Durable knowledge | `brain/` | Show a diff + get approval |
| Deliverables | `output/` | Confirm create/edit/delete |
| Structured-data **structure** (new table/column) | `data/` | Confirm (plain language) |

Logging to disk (and summarizing in chat) keeps the chat clean. The brain
and output are gated because they're durable. Structured data lives in
plain JSON tables under `data/`, accessed only through the bundled
`data.py` helper (queries run over a throwaway in-memory copy; writes
snapshot first). Records that fit existing columns are free; only structure
changes are confirmed.

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| `sidekick` | Automatic, on any work | Project detection + the three write disciplines. The backbone. |
| `sidekick-init` | `/sidekick-init` | Multiple-choice setup; writes settings; scaffolds the first project. |
| `sidekick-triage` | Scheduled / `/sidekick-triage` | Read-only scan of email + chat + calendar → `_triage/`. |
| `sidekick-checkin` | `/sidekick-checkin` | Walks all projects, cross-references triage + calendar, proposes actions. |
| `sidekick-archive` | `/sidekick-archive` | Moves a project to `_archive/` (never deletes). |
| `sidekick-status` | `/sidekick-status` | Read-only cross-project overview — where everything stands. |
| `sidekick-find` | `/sidekick-find` | Read-only cross-project recall — search brains, logs, agendas, data. |
| `sidekick-report` | `/sidekick-report` | Saved reports + tabbed HTML dashboards over a project's `data/` store (via `data.py query`). |

## Install in Cowork

Sidekick installs from its **private GitHub repo** (`boezelaere/sidekick`),
which is its own **marketplace** (it ships `.claude-plugin/marketplace.json`):

1. **Add the marketplace**, then **install the plugin**. Point Cowork at the
   GitHub repo `boezelaere/sidekick` as a marketplace, then install the
   **`sidekick`** plugin from it. (Adding a plugin repo directly fails — Cowork
   adds *marketplaces*, which then list installable plugins.)
2. **Run `/sidekick-init`** (or just ask, e.g. *"set up my Sidekick
   workspace"*) — a short multiple-choice setup for your role, chat language,
   default output language, and which connections you want. It writes
   `sidekick.settings.md` and scaffolds your first project. It does **not**
   turn any connector on.
3. **Enable connectors** you said yes to (email / messages / storage /
   calendar) in **Cowork's connector settings** — the plugin only records
   intent; you enable the actual connections. If you turned on **output sync**,
   set **Output sync base path** to a mounted/synced Drive/OneDrive folder
   (e.g. `G:\My Drive\sidekick`): the bundled `sync.py` CLI keeps each project's
   `output/` in step **both ways** with `<base>\<slug>\output\` via plain file
   copies (binary-safe, additive; conflicts ask you which version wins). No base
   path ⇒ sync stays idle; files are never routed through the chat.
4. **Schedule triage (optional):** attach `sidekick-triage` to a Cowork
   **scheduled task** and pick a frequency (e.g. daily). It writes findings
   to `_triage/`; the plugin does not set the frequency.
5. **Just start working** — the always-on `sidekick` skill picks the right
   project and keeps everything structured. Run `/sidekick-checkin` to
   review across projects, `/sidekick-status` for a read-only overview,
   `/sidekick-find` to recall across projects, `/sidekick-report` to turn a
   project's data into a dashboard, `/sidekick-archive` to retire one.

## For contributors

- **Validate structure** before changing or releasing the plugin:
  ```
  node scripts/validate-structure.mjs
  ```
  It checks the manifest, every skill's frontmatter, and all reference
  paths, exiting non-zero on any failure.
- **Manual tests:** [`docs/MANUAL-TESTS.md`](docs/MANUAL-TESTS.md) is a
  ~30-minute human-judged checklist for verifying behavior in a disposable
  Cowork sandbox.

## Design

The full design is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) —
the source of truth. Every skill is derived from it.

A plugin-wide principle: when Sidekick puts a choice to you, it asks with
**multiple choice** by default (tapping beats typing in Cowork). Open
questions are reserved for free-form answers like a project name or a
reply body.

## Languages

Sidekick separates **chat language** (how it talks to you) from **default
output language** (the language of deliverables). They can differ — chat
in Dutch, documents in English, for example.

## Status

**0.9.0** — Claude Cowork plugin (id `sidekick`; commands are `/sidekick-*`).
Installed from the private GitHub repo; hardened and documented across the
`plan/` units. Cowork command support follows the working SolidCortex pattern:
flat `commands/<name>.md` files give the typed `/sidekick-init` etc. (the
install-blocker through 0.2.5 was a malformed `repository` manifest field — an
object where the schema needs a string — fixed in 0.2.6). Since then: a
file-based `data/` store via the `data.py` helper (0.3.x), a read-only layer
(`/sidekick-status`, `/sidekick-find`, 0.4.0), and a presentation layer
(`/sidekick-report` — saved reports + tabbed HTML dashboards, 0.5.0), and an
explicit **subproject/area** concept (areas inside a project, never nested
projects, 0.6.0), and optional **two-way output sync** — keep each project's
`output/` in step both ways with `<base path>\<slug>\output\` on a mounted
storage folder (additive, conflicts ask; only yes/no + a base path recorded in
settings). Sync evolved fast under testing: one-way mirror (0.7.0) → two-way (0.8.0) → the
transport problem surfaced (0.8.1: pushing a binary made the model base64 it,
a 5-minute hang) → a dedicated `sync.py` CLI doing plain file copies to a
mounted **base path**, no bytes through the model (0.9.0). Run the manual-test
checklist in Cowork before wider rollout.
