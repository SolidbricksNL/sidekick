# Sidekick — development plan

Master tracker for hardening, testing, and shipping the **Sidekick** Cowork
plugin. Each unit below is a self-contained plan file under `plan/` that a later
session can open and execute on its own. Work them roughly in order; the
**Depends on** column is the real constraint.

`docs/ARCHITECTURE.md` is the single source of truth. Plan files propose edits;
they do not silently change the design. Anything ambiguous is recorded as an
**open question** in the relevant plan file (and summarized at the bottom here).

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
| 13 | [13-docs-and-release.md](13-docs-and-release.md) | Final docs pass, INSTALL section, version bump + git tag, rollout note. | 01–12 | [ ] not started |

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

## Collected open questions (need the user's decision before/while executing)

These are aggregated from the individual plan files. Resolve the design-level
ones before the units that depend on them run.

1. **Cowork manifest required fields** (plan 01) — is `name`/`version`/
   `description`/`author` the complete required set, or does Cowork want more
   (license, homepage, explicit skills/commands)? Are `/sidekick-*` commands
   auto-derived from skill names?
2. **Cross-skill template reads** (plans 01, 03, 04) — can `sidekick-init` read
   the `sidekick` skill's `references/*-template.md` at runtime, or must those
   templates be duplicated under `sidekick-init/references/`? (The init body's
   `agenda-template.md` reference currently resolves to a non-existent path.)
3. **SQLite execution mechanism** (plan 06) — how does Sidekick actually run
   SQL against `data.sqlite` in Cowork (shell `sqlite3`, a tool, an MCP)? If
   none is guaranteed, what's the fallback?
4. **Connector / MCP mechanism** (plans 03, 08, 09) — are email/chat/calendar
   exposed as native Cowork connectors, MCP servers, or both? This defines what
   "enable the connector" means and how triage/check-in read and (for replies)
   write.
5. **Filesystem move primitive** (plan 10) — is a true `mv`/rename available for
   archiving, or only copy+delete (which needs a careful verify-then-remove
   sequence to honor "never delete")?
6. **ARCHITECTURE §13 sync** (plans 03, 13) — mark the now-resolved open items
   (questionnaire wording, agenda template) and confirm what stays deferred
   (`.mcp.json`).
7. **Release target + distribution** (plan 13) — ship as `0.2.0` or `1.0.0`,
   and how are Cowork plugins distributed/installed internally (git URL,
   marketplace, zipped artifact)?
8. **GitHub account / ownership** (repo setup) — the repo was created under the
   authenticated GitHub account **`boezelaere`** (`github.com/boezelaere/sidekick`,
   private), while the session user is `wouter.boelaars@visma.com`. Confirm this
   is the intended owner, or move it to a Visma org.
