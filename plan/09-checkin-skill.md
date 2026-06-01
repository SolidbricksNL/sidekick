# Check-in skill

**Status:** not started
**Depends on:** 04-project-model-and-scaffolding, 05-write-disciplines-enforcement, 07-brain-protocol, 08-triage-skill

## Goal
"Done" means the user-initiated check-in is finalized: it walks all
non-archived projects, cross-references the latest triage findings and the
calendar, proposes actions as quick multiple-choice items, drafts replies (never
sends unprompted), routes each approved action through the correct gatekeeper,
and logs what it processed. The acceptance artifact is a **scripted walkthrough**
over a 2–3 project sandbox showing proposals → approvals → correct writes.

## Context
- `ARCHITECTURE.md` §11 (check-in layer).
- `skills/sidekick-checkin/SKILL.md`.
- Consumes triage output (plan 08) and agendas (plan 04); applies gatekeepers
  (plan 05), brain protocol (plan 07), database discipline (plan 06).

## Tasks
1. [ ] Confirm preconditions: read settings (chat lang, output lang, connected
   calendar); list non-archived `projects/`; read latest `_triage/` file(s) since
   the previous check-in (and proceed gracefully if none); read near-term
   calendar if connected (read-only).
2. [ ] Confirm the per-project walk: read `agenda.md` + brain index; pull triage
   findings tagged to the project; pull related calendar items; synthesize
   moved/stuck/new/due; propose concrete actions, each tagged with type +
   gatekeeper (update brain / do action / create deliverable / reply draft /
   agenda / calendar-note).
3. [ ] Confirm proposals are presented as quick multiple-choice (Yes / No / Edit
   first) so the user can run through them by tapping (ties to plan 11).
4. [ ] Confirm the "Unassigned / new project?" handling: present together; offer
   start-new-project (hand off to canonical scaffolding) / attach-to-existing /
   ignore.
5. [ ] Confirm acting-on-approvals routes correctly:
   - Brain → show diff, write after approval, move processed source to
     `archive/`.
   - Output / database structure → confirm, then create/edit; record output.
   - Agenda → update directly (free bookkeeping).
   - Replies → draft in the right language; send ONLY if the user explicitly said
     so in this chat; never send unprompted.
   - Log → record what the check-in processed in the project's `log/`
     (`YYYYMMDD-checkin.md`), freely.
6. [ ] Confirm the closing wrap-up is a short steering summary (per-project
   decided/open + cross-project flags) and that each touched `agenda.md` is left
   clean for next time — not a wall of text.
7. [ ] **Build the scripted walkthrough** (write it into this plan as the
   artifact): a 2–3 project sandbox with a sample `_triage/` file, run the
   check-in, show the multiple-choice proposals, simulate the user's
   approvals/declines, and show exactly which writes happen and through which
   gatekeeper, plus the resulting `log/` and `agenda.md` updates.

## Acceptance criteria
- A scripted 2–3 project walkthrough exists: proposals → approvals → correct,
  correctly-gated writes, with the resulting log + agenda changes shown.
- "Reply = draft only unless explicitly approved to send" is confirmed
  unambiguous.
- Every approved action type is shown routing through its correct gatekeeper.
- The wrap-up + agenda-cleanup behavior is confirmed.

## Notes / open questions (reply mechanism resolved 2026-06-01)
- **Reply sending — RESOLVED (gated).** Replies are drafted only; sending uses a
  connector the **user** enabled, and only after an explicit in-chat "send it".
  Check-in never enables a connector. If no send-capable connector is connected,
  check-in leaves the draft (in the chat or `output/`) for the user to send
  manually. It never sends unprompted.
- **Triage freshness.** Define "latest triage since the previous check-in" when
  several triage files exist — read the newest, or all unprocessed ones? Decide
  and document so findings aren't missed or double-counted.
- **Calendar correlation.** Matching calendar items to a project is heuristic
  (topic/people). Note it's best-effort and surfaced for the user to confirm.
