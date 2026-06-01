# Brain protocol

**Status:** not started
**Depends on:** 04-project-model-and-scaffolding, 05-write-disciplines-enforcement

## Goal
"Done" means the per-project brain protocol is verified against the supplied
method: distill-not-copy; original to `archive/`; always-diff-before-write; no
new brain files without asking; update existing lines rather than stacking
contradictory versions. The acceptance artifact is a **worked example** that
distills one shared document into a brain file, shows the diff that would be
presented for approval, and lands the original in `archive/`.

## Context
- `ARCHITECTURE.md` §5 (brain layer).
- `skills/sidekick/references/brain-protocol.md` (full protocol).
- `skills/sidekick/SKILL.md` ("Discipline 2 — Brain").
- The gatekeeper (diff + approval) comes from plan 05; `data-model.md` is a
  brain file but its content rules live in plan 06.

## Tasks
1. [ ] Confirm the four rules are stated and consistent across `brain-protocol.md`,
   the main SKILL.md, and ARCHITECTURE §5: distill-don't-copy; always show a
   diff; no new files without asking; update existing lines.
2. [ ] Confirm the layer model (brain = permanent memory; log = process;
   archive = originals; output = deliverables) and the "no inbox folder — input
   arrives via chat" rule.
3. [ ] Confirm the cycle: SHARE → DISTILL (diff+approval) → LOG → USE → DELIVER
   → WRITE BACK, and that `CLAUDE.md` lists which brain files to read at session
   start.
4. [ ] Confirm brain file-splitting guidance (start with 1–2 files; split when
   too large) and the typical file names (`<topic>.md`, `landscape.md`,
   `links.md`, `decisions.md`, `data-model.md`).
5. [ ] Define precisely what "show a diff" means operationally for a brand-new
   brain file (the whole file is the diff) vs an edit to an existing file (a
   line-level diff), so approval is consistent in both cases.
6. [ ] Build the **worked example** (write it into this plan as the artifact):
   - User shares a strategy memo in chat.
   - Sidekick extracts 3–4 durable points; proposes adding them to
     `brain/<topic>.md`; shows the diff (new file → whole content shown).
   - On approval, writes the brain file AND moves the original memo into
     `archive/`.
   - A later session updates one fact → shows a line-level diff that amends the
     existing line rather than appending a contradictory one.
7. [ ] Confirm the archive step (original → `archive/`) is tied to the brain
   write so originals are never lost and never duplicated into the brain.

## Acceptance criteria
- A written worked example exists showing: shared doc → distilled brain points →
  presented diff → approval → brain write + original moved to `archive/`.
- A second step shows updating an existing line (amend, not stack) with its
  diff.
- "Show a diff" is defined for both new-file and existing-file cases.
- The four brain rules are confirmed consistent across all three sources.

## Notes / open questions
- **Diff presentation in Cowork.** Confirm the practical way to "show a diff" to
  a non-technical user in Cowork (a before/after block, a unified diff, a plain
  "I'll change X to Y" summary). The protocol says diff; the tone must stay
  non-technical per ARCHITECTURE §2.
- **Archive vs Cowork connectors.** When a "shared document" actually lives in a
  connected storage (Drive/OneDrive) rather than the chat, define what "move the
  original to archive/" means (copy a local snapshot vs reference). Likely: keep
  a local copy in `archive/`. Flag for confirmation.
