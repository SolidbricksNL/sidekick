# Write-disciplines enforcement

**Status:** not started
**Depends on:** 02-skill-prompt-review, 04-project-model-and-scaffolding

## Goal
"Done" means the three write disciplines are crisp and testable, and every
write action in every skill is mapped to its correct gatekeeper. The disciplines:
log = free (write to disk, summarize in chat); brain = diff + approval; output =
confirm create/edit/delete; database = confirm STRUCTURE only, records that fit
the schema are free. The acceptance artifact is a single **matrix** mapping
every write action across all five skills to its gatekeeper, with any
mis-gated or un-gated write flagged.

## Context
- `ARCHITECTURE.md` §2 (three disciplines table), §4 (database), §5 (brain),
  §6 (log), §7 (output).
- `skills/sidekick/references/write-disciplines.md` (the decision rule).
- All five `SKILL.md` files — each performs or proposes writes.
- Overlaps: brain detail is plan 07; database detail is plan 06; this plan owns
  the cross-skill matrix and the top-level rule.

## Tasks
1. [ ] Restate the decision rule crisply (from `write-disciplines.md`) and
   confirm it matches ARCHITECTURE §2 exactly (including the 3b database row and
   the "records that fit are free" carve-out).
2. [ ] Enumerate **every write action** each skill performs or proposes:
   - `sidekick`: log files, brain distillation, output deliverables, sqlite
     structure + records, agenda updates, project scaffolding.
   - `sidekick-init`: settings file, first-project scaffold, root system folders.
   - `sidekick-triage`: ONLY `_triage/YYYYMMDD-triage.md` (nothing else).
   - `sidekick-checkin`: brain (via approval), output (via confirm), agenda
     (free bookkeeping), reply drafts (no send without explicit ok), log of what
     it processed.
   - `sidekick-archive`: move project folder; no other writes; never deletes.
3. [ ] Build the **gatekeeper matrix**: rows = write actions, columns = {target
   location, gatekeeper required, where stated in the skill, ARCHITECTURE ref}.
4. [ ] Flag every cell where a skill could write without the right gatekeeper,
   or where the wording is ambiguous about which gatekeeper applies. Capture
   each as a proposed wording fix (defer application; coordinate with plan 02).
5. [ ] Special checks:
   - Agenda writes are classified as free bookkeeping (log-like), not gated —
     confirm this is intended and stated consistently (checkin says so).
   - Settings file write (init) — classify its gatekeeper (it's a confirmed
     write after summary; document it).
   - Triage writing ONLY to `_triage/` — confirm nothing in its body permits any
     other write.
6. [ ] Confirm the "log to disk, summarize in chat — never the reverse" rule is
   present wherever substantive output could otherwise leak into chat.

## Acceptance criteria
- A single gatekeeper matrix covering every write action across all five skills
  exists, each row tagged with its gatekeeper and ARCHITECTURE reference.
- No write action is left un-gated except those intentionally free (log, agenda
  bookkeeping, sqlite records that fit, triage's single `_triage/` file).
- Every ambiguous or mis-gated write has a concrete proposed wording fix
  recorded (not yet applied).

## Notes / open questions
- **Agenda classification.** Is `agenda.md` formally part of the "log = free"
  discipline, or a fourth lightweight free-write category? It's user-facing but
  bookkeeping. Confirm the intended classification so the matrix is consistent.
- **Settings + scaffold writes.** Init's settings write and scaffolding are
  one-time setup writes done after an explicit summary+confirm. Confirm they're
  treated as "confirmed" writes and don't need the brain-style diff.
- **Chat-leak enforcement.** The "summarize in chat, write to disk" rule is a
  behavior, not a file boundary — note that it can only be verified by the
  manual walkthroughs (plan 12), not by a script.
