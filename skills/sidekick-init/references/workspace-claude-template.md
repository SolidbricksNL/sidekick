# Sidekick workspace

> Cowork auto-loads this file into every session and re-injects it after
> compaction. It is the always-on contract for this workspace. Keep it short.

This is a **Sidekick** workspace. All work is structured into projects;
nothing loose accumulates in the root.

## Before doing any work

1. Read `sidekick.settings.md` (role, chat language, default output language)
   and apply it: chat in the chat language, write deliverables in the output
   language, adopt the role.
2. Invoke the **sidekick-core** skill and follow its session-start protocol
   (pick or create the project, then read that project's `CLAUDE.md` +
   `agenda.md`). If the skill is unavailable, still follow the rules below.

## Hard rule — nothing loose in the workspace root

The ONLY files that belong in this root are `sidekick.settings.md` and this
`CLAUDE.md`. The only folders are `projects/`, `_triage/`, `_archive/`.
**Never write a document, script, note, draft, or data file to the root.**
Everything belongs to a project under `projects/<slug>/`:

- work-in-progress, notes, drafts → `projects/<slug>/log/` (write freely)
- durable distilled knowledge → `projects/<slug>/brain/` (show a diff, write after approval)
- deliverables (docs, sheets, decks) → `projects/<slug>/output/` (confirm before create/edit/delete)
- structured or tabular data → `projects/<slug>/data/` via `scripts/data.py` (confirm a structure change)

If you are unsure which project something belongs to, **ask** with a tappable
choice — never default to writing in the root.

## Projects

Each project is a **direct child** of `projects/` with its own `CLAUDE.md` +
`agenda.md`; read those when you enter a project. A strand of work *within* a
project is an **area** (`brain/<sub>/` + `output/<sub>/`), never a new
top-level or nested project.
