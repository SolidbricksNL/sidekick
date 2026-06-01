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
│       └── data.sqlite       # structured data     (structure = confirm)
└── _archive/projects/        # archived projects (moved, never deleted)
```

## The three write disciplines

| What | Where | Gatekeeper |
|---|---|---|
| Process, work-in-progress | `log/` | Write freely |
| Durable knowledge | `brain/` | Show a diff + get approval |
| Deliverables | `output/` | Confirm create/edit/delete |
| Database **structure** | `data.sqlite` | Confirm (plain language) |

Logging to disk (and summarizing in chat) keeps the chat clean. The brain
and output are gated because they're durable. Database records that fit
the schema are free; only structure changes are confirmed.

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| `sidekick` | Automatic, on any work | Project detection + the three write disciplines. The backbone. |
| `sidekick-init` | `/sidekick-init` | Multiple-choice setup; writes settings; scaffolds the first project. |
| `sidekick-triage` | Scheduled / `/sidekick-triage` | Read-only scan of email + chat + calendar → `_triage/`. |
| `sidekick-checkin` | `/sidekick-checkin` | Walks all projects, cross-references triage + calendar, proposes actions. |
| `sidekick-archive` | `/sidekick-archive` | Moves a project to `_archive/` (never deletes). |

## Install in Cowork

Sidekick installs from its **private GitHub repo** (`boezelaere/sidekick`):

1. **Add the plugin** in Cowork from the GitHub repository.
2. **Run `/sidekick-init`** — a short multiple-choice setup for your role,
   chat language, default output language, and which connections you want.
   It writes `sidekick.settings.md` and scaffolds your first project. It
   does **not** turn any connector on.
3. **Enable connectors** you said yes to (email / messages / storage /
   calendar) in **Cowork's connector settings** — the plugin only records
   intent; you enable the actual connections.
4. **Schedule triage (optional):** attach `sidekick-triage` to a Cowork
   **scheduled task** and pick a frequency (e.g. daily). It writes findings
   to `_triage/`; the plugin does not set the frequency.
5. **Just start working** — the always-on `sidekick` skill picks the right
   project and keeps everything structured. Run `/sidekick-checkin` to
   review across projects, `/sidekick-archive` to retire one.

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

**0.2.0** — Claude Cowork plugin. Installed from the private GitHub repo;
hardened and documented across the `plan/` units. Run the manual-test
checklist in Cowork before wider rollout.
