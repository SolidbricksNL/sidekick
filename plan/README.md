# Sidekick — development plan

Master tracker for hardening, testing, and shipping the **Sidekick** Cowork
plugin. Each unit below is a self-contained plan file under `plan/` that a later
session can open and execute on its own. Work them roughly in order; the
**Depends on** column is the real constraint.

`docs/ARCHITECTURE.md` is the single source of truth. Plan files propose edits;
they do not silently change the design. The open questions raised during
planning have been **resolved** (see the decisions section below).

## Execution order

| # | Plan file | Purpose | Depends on | Status |
|---|-----------|---------|------------|--------|
| 01 | [01-structure-validation.md](01-structure-validation.md) | Verify plugin structure for Cowork; add a re-runnable validator script. | — | [ ] not started |
| 02 | [02-skill-prompt-review.md](02-skill-prompt-review.md) | Review each SKILL.md as a prompt (triggers, gatekeeper clarity, contradictions); propose diffs, don't apply. | 01 | [ ] not started |
| 03 | [03-settings-and-init-flow.md](03-settings-and-init-flow.md) | Validate the init questionnaire end to end; finalize the `sidekick.settings.md` field spec. | 01, 02 | [ ] not started |
| 04 | [04-project-model-and-scaffolding.md](04-project-model-and-scaffolding.md) | Nail down the on-disk project model + folder contract; finalize the CLAUDE.md and agenda templates. | 01, 03 | [ ] not started |
| 05 | [05-write-disciplines-enforcement.md](05-write-disciplines-enforcement.md) | Make the three disciplines testable; build a gatekeeper matrix across all skills. | 02, 04 | [ ] not started |
| 06 | [06-database-discipline.md](06-database-discipline.md) | Finalize the SQLite layer; worked example of propose→create→document→extend. | 04, 05 | [ ] not started |
| 07 | [07-brain-protocol.md](07-brain-protocol.md) | Verify the brain protocol; worked example of a distillation with diff + archive. | 04, 05 | [ ] not started |
| 08 | [08-triage-skill.md](08-triage-skill.md) | Harden scheduled triage (read-only, `_triage/`-only, injection-safe); sample output + safety checklist. | 02, 04, 05 | [ ] not started |
| 09 | [09-checkin-skill.md](09-checkin-skill.md) | Finalize the check-in; scripted 2–3 project walkthrough proposals→approvals→writes. | 04, 05, 07, 08 | [ ] not started |
| 10 | [10-archive-skill.md](10-archive-skill.md) | Verify archive = move-never-delete + restore; scripted move-and-restore. | 04 | [ ] not started |
| 11 | [11-interaction-style.md](11-interaction-style.md) | Ensure plugin-wide multiple-choice is applied everywhere; choice-point checklist. | 02 | [ ] not started |
| 12 | [12-manual-test-walkthroughs.md](12-manual-test-walkthroughs.md) | End-to-end human-judged scenarios in a disposable Cowork sandbox; ~30-min checklist. | 03–11 | [ ] not started |
| 13 | [13-docs-and-release.md](13-docs-and-release.md) | Final docs pass, INSTALL section, version bump to 0.2.0 + git tag, rollout note. | 01–12 | [ ] not started |

Status legend: `[ ] not started` · `[~] in progress` · `[x] done`. Update both
this row and the **Status:** line at the top of the plan file when a unit moves.

## Dependency shape (why this order)

- **01** (structure) gates everything — a broken layout invalidates later work.
- **02** (prompt review) precedes the per-topic plans, since they may rely on
  proposed wording fixes.
- **03 → 04**: settings before the project model (the project CLAUDE.md points
  at settings; init and the always-on skill must scaffold identically).
- **05** (disciplines matrix) sits before the per-discipline deep dives
  **06** (database) and **07** (brain), and before the skills that perform gated
  writes **08**/**09**.
- **08 → 09**: triage produces what check-in consumes.
- **10** (archive) only needs the project model.
- **11** (interaction style) only needs the prompt review.
- **12** (manual tests) needs every skill plan finalized.
- **13** (release) is last and ships what the rest hardened.

## Validator

Plan 01 introduces `scripts/validate-structure.*` — a zero-dependency checker for
the plugin's structural correctness (manifest, skill frontmatter, reference
paths, dead links). Run it before starting a unit and again before release
(plan 13).

## Resolved decisions (user review, 2026-06-01)

The open questions raised during planning are resolved. Decisions below are
binding for execution; the few residual items are verify-on-install checks
folded into plans 02 and 12.

1. **Cowork manifest** (plan 01) — RESOLVED. Cowork uses the **same plugin
   format as Claude Code**. In `plugin.json` only `name` is required; the current
   manifest (`name`, `version`, `description`, `author{name}`) is **valid as-is**.
   Skills are auto-discovered from `skills/`; no declaration needed. Optional
   polish (`repository`, `license`, `keywords`, `homepage`) is deferred to plan
   13. **Verify item (→ plan 12):** the exact USER-typed command name is
   uncertain. Docs say namespaced `/sidekick:<skill>`; Claude Code bugs #22063 (a
   `name:` in frontmatter → bare `/sidekick-init`) and #41842 (`skills/` may not
   register as `/` commands; model invocation still works) point other ways, and
   Cowork is undocumented. The always-on skill + all cross-skill references work
   by model invocation regardless, so only the typed name is at stake. Settle it
   by installing in Cowork and reading the `/` menu (plan 12); fallback is thin
   `commands/<skill>.md` wrappers. Don't rewrite command strings until then.
2. **Cross-skill templates** (plans 01, 03, 04) — RESOLVED: **no duplication.**
   Shared templates stay in `skills/sidekick/references/`; other skills reference
   them via the `../sidekick/references/...` relative path already used by
   triage/checkin/archive for `interaction-style.md`. The whole plugin is copied
   to the cache as one unit on install, so within-plugin `../` paths resolve.
   Init's two broken template references were fixed to this convention **in this
   pass**. Hedge (→ plan 12): if Cowork sandboxes skills per-directory, fall back
   to a plugin-root `shared-references/` dir (a mechanical move).
3. **SQLite execution** (plan 06) — RESOLVED: run SQLite via Python's **stdlib
   `sqlite3` module** (Python 3.11 confirmed in-env; the `sqlite3` CLI is NOT
   present and not guaranteed in Cowork). A small helper script **bundled in the
   plugin** does create/alter/query; per-project databases stay at
   `projects/<slug>/data.sqlite`. No external dependency.
4. **Connectors** (plans 03, 08, 09) — RESOLVED: the **user** installs/enables
   connectors in Cowork. Skills never enable anything — they record intent (init)
   and **guide** the user to enable connectors. No `.mcp.json` auto-config.
5. **Archive move primitive** (plan 10) — RESOLVED: prefer a true rename/move; if
   the runtime lacks atomic rename, **copy → verify the copy is complete → only
   then remove the source**. The source is never removed before the copy is
   verified, so "never delete" always holds.
6. **ARCHITECTURE §13 sync** (plans 03, 13) — YES. Mark the questionnaire wording
   and agenda template as resolved; drop `.mcp.json` auto-config (superseded by
   decision 4). Applied in plan 13's docs pass.
7. **Release** (plan 13) — Ship as **0.2.0**. Distribution: install from the
   private GitHub repo first; later create an organization plugin and open it
   public from GitHub once we're happy with it.
8. **Repo ownership** — CONFIRMED: `github.com/boezelaere/sidekick` (private) is
   the intended owner.
