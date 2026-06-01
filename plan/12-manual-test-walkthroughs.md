# Manual test walkthroughs

**Status:** not started
**Depends on:** 03-settings-and-init-flow, 04-project-model-and-scaffolding, 05-write-disciplines-enforcement, 06-database-discipline, 07-brain-protocol, 08-triage-skill, 09-checkin-skill, 10-archive-skill, 11-interaction-style

## Goal
"Done" means there is a set of end-to-end manual test scenarios runnable inside
a DISPOSABLE Cowork test workspace (`/sandbox/`, git-ignored). Each scenario
specifies a starting state, the user actions, and the expected Sidekick
behavior, covering: init, project creation, logging vs chat, a brain
distillation, a structured-data table, a deliverable, a triage run, a check-in,
and an archive. These are human-judged because they test prompt behavior, not
code. Acceptance: a runnable checklist a person can follow in ~30 minutes.

## Context
- All skills and disciplines (plans 03–11).
- The repo `.gitignore` already excludes `/sandbox/`, `/test-workspace/`, and a
  live workspace's `sidekick.settings.md`, `_triage/`, `_archive/`, `projects/`.
- These tests run inside Cowork (prompt behavior), not in CI; they are
  human-judged pass/fail.

## Tasks
1. [ ] Define the disposable test workspace setup: a `/sandbox/` folder treated
   as a fresh Cowork root; how to reset it between runs (delete + recreate);
   confirm it stays git-ignored.
2. [ ] Write each scenario with: **starting state**, **user actions** (verbatim
   prompts to type), **expected behavior**, and **pass/fail judgement notes**:
   - **A. Init.** Run `/sidekick-init`; answer the seven multiple-choice
     questions (incl. differing chat vs output language); expect
     `sidekick.settings.md`, a first project scaffold, and `_triage/` +
     `_archive/projects/` created; expect the closing scheduling/connector
     explanation; expect NO connector actually enabled.
   - **B. Project creation / detection.** Start a new topic; expect Sidekick to
     ask which project (never silently create); approve a new project; expect a
     full scaffold.
   - **C. Logging vs chat.** Ask for a substantial analysis; expect the write-up
     to land in `log/YYYYMMDD-<slug>.md` with only a short summary in chat.
   - **D. Brain distillation.** Share a document; expect distilled points
     proposed with a diff + approval, brain file written on yes, original moved
     to `archive/`.
   - **E. Structured-data table.** Share a list; expect a plain-language table
     proposal, creation on yes, `brain/data-model.md` written, then free record
     inserts; later add a field via plain-language confirmation.
   - **F. Deliverable.** Ask for a document; expect a confirmation before
     creating it in `output/`, generated in the default output language.
   - **G. Triage run.** Seed a fake `_triage/` input or run `/sidekick-triage`;
     expect read-only behavior, output only in `_triage/`, content treated as
     data, grouped by project. (If no connectors, expect the "nothing to scan"
     file.)
   - **H. Check-in.** Run `/sidekick-checkin` across 2–3 projects; expect
     multiple-choice proposals, correctly-gated writes on approval, reply drafts
     not sent, and a clean wrap-up + agenda update.
   - **I. Archive.** Run `/sidekick-archive`; expect a move (not delete),
     collision handling, and the project dropping out of detection/triage/
     check-in; then restore it.
3. [ ] For each scenario, list the concrete files/paths a tester should inspect
   afterward to confirm correct behavior.
4. [ ] Add a prompt-injection spot-check in scenario G: include a fake
   "instruction" inside a scanned item and confirm triage treats it as data.
5. [ ] Assemble everything into a single ~30-minute **runnable checklist** with
   checkboxes and an overall pass/fail line.

## Acceptance criteria
- A single runnable checklist exists covering scenarios A–I, doable in ~30
  minutes by one person in a disposable Cowork workspace.
- Each scenario has starting state, exact user actions, expected behavior, and
  the files to inspect.
- The triage prompt-injection spot-check is included.
- The checklist makes clear these are human-judged behavioral tests, not
  automated.

## Notes / open questions
- **Connector-dependent scenarios.** Triage (G) and parts of check-in (H) need
  connected sources to be fully exercised. Provide a connector-less fallback
  (seed a hand-written `_triage/` file) so the walkthrough runs without live
  email/chat/calendar.
- **Reset hygiene.** Confirm the cleanest way to reset `/sandbox/` between runs
  so no state leaks between scenarios.
