# Project model and scaffolding

**Status:** not started
**Depends on:** 01-structure-validation, 03-settings-and-init-flow

## Goal
"Done" means the on-disk project model is nailed down as an unambiguous folder
contract: the exact scaffold of `projects/<slug>/` (CLAUDE.md, agenda.md,
brain/, log/, archive/, output/, and lazily-created data.sqlite), slug
conventions, the root-level `_triage/` and `_archive/projects/` folders, and
project-detection behavior (match → confirm; doubt → ask; never silently
create). The `project-claude-template.md` and `agenda-template.md` are
finalized.

## Context
- `ARCHITECTURE.md` §3 (project model), §3.0 (scaffold), §3.1 (detection),
  §3.2 (slug), §3.3 (archiving).
- `skills/sidekick/SKILL.md` ("Project detection" + "Scaffolding a project").
- `skills/sidekick/references/project-claude-template.md`.
- `skills/sidekick/references/agenda-template.md`.
- Both init (plan 03) and the always-on skill scaffold projects; they must agree.

## Tasks
1. [ ] Write the canonical **folder contract** for a project, listing every path
   created on scaffold and its initial state:
   - `projects/<slug>/CLAUDE.md` (seeded from template, project name filled).
   - `projects/<slug>/agenda.md` (seeded from template).
   - `projects/<slug>/brain/` (empty until first distillation).
   - `projects/<slug>/log/` (empty).
   - `projects/<slug>/archive/` (empty).
   - `projects/<slug>/output/` (empty).
   - `projects/<slug>/data.sqlite` — NOT created on scaffold; lazy.
   - Root system folders: `_triage/`, `_archive/projects/`.
2. [ ] Decide how empty directories are represented on disk so they survive in
   git/Cowork (e.g. a `.gitkeep`), and whether the live workspace needs them at
   all (the live workspace is git-ignored — see repo `.gitignore`). Document the
   decision; keep templates as the source of truth, not committed sample dirs.
3. [ ] Confirm slug rules: `kebab-case`, short, descriptive (`core-roadmap`,
   `client-bpd`, `q3-board-prep`). Define how a free-text project name maps to a
   slug (lowercase, spaces→hyphens, strip punctuation, collision suffix).
4. [ ] Confirm project-detection behavior matches ARCHITECTURE §3.1 exactly:
   list `projects/`, read each `agenda.md` + brain index, match intent, confirm
   on clear match, ask on doubt, scaffold only on explicit approval, **never
   silently create**. Confirm archived projects are excluded from detection.
5. [ ] **Finalize `project-claude-template.md`**: verify the relative path
   `../../sidekick.settings.md` is correct from `projects/<slug>/CLAUDE.md`,
   the "read at session start" list, the write-disciplines reminder, and the
   `{{PROJECT_NAME}}` / `{{MAIN_TOPIC}}` placeholders. Propose any wording fix.
6. [ ] **Finalize `agenda-template.md`**: confirm the sections (Open items /
   Waiting on / Recently done / Notes for the next check-in), the status
   vocabulary (todo/doing/waiting/done), and the `{{PROJECT_NAME}}`/`{{DATE}}`
   placeholders serve the check-in (plan 09) well.
7. [ ] Reconcile init's scaffolding (plan 03) with the always-on skill's
   scaffolding so they produce byte-identical structure from the same templates.
8. [ ] Cross-check that the template-location decision from plan 03 (duplicate vs
   cross-reference) is reflected here.

## Acceptance criteria
- A documented, unambiguous folder contract exists that both init and the
  always-on skill follow identically.
- `project-claude-template.md` and `agenda-template.md` are finalized (or have
  concrete proposed diffs) with correct relative paths and placeholders.
- Slug derivation rules (including collision handling) are written down.
- Project detection is confirmed to never silently create a project and to
  exclude archived projects.

## Notes / open questions
- **Empty-folder persistence.** The live workspace is git-ignored, so empty
  scaffold dirs aren't a git concern there; but confirm Cowork tolerates empty
  `brain/`/`log/`/`archive/`/`output/` dirs, or whether each should get a tiny
  placeholder README on scaffold.
- **Template location** (shared with plan 01 + plan 03): does init read the
  `sidekick` skill's `references/*-template.md`, or do we duplicate them under
  `sidekick-init/references/`? Decide once; apply in both plans.
- **`{{MAIN_TOPIC}}` at scaffold time.** The CLAUDE.md template points at
  `brain/{{MAIN_TOPIC}}.md` before any brain file exists. Decide whether to fill
  a sensible default at scaffold, leave the placeholder, or comment it out until
  the first brain file is created.
