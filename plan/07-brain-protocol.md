# Brain protocol

**Status:** done (worked example + show-a-diff definition written)
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
1. [x] Confirm the four rules are stated and consistent across `brain-protocol.md`,
   the main SKILL.md, and ARCHITECTURE §5: distill-don't-copy; always show a
   diff; no new files without asking; update existing lines.
2. [x] Confirm the layer model (brain = permanent memory; log = process;
   archive = originals; output = deliverables) and the "no inbox folder — input
   arrives via chat" rule.
3. [x] Confirm the cycle: SHARE → DISTILL (diff+approval) → LOG → USE → DELIVER
   → WRITE BACK, and that `CLAUDE.md` lists which brain files to read at session
   start.
4. [x] Confirm brain file-splitting guidance (start with 1–2 files; split when
   too large) and the typical file names (`<topic>.md`, `landscape.md`,
   `links.md`, `decisions.md`, `data-model.md`).
5. [x] Define precisely what "show a diff" means operationally for a brand-new
   brain file (the whole file is the diff) vs an edit to an existing file (a
   line-level diff), so approval is consistent in both cases.
6. [x] Build the **worked example** (write it into this plan as the artifact):
   - User shares a strategy memo in chat.
   - Sidekick extracts 3–4 durable points; proposes adding them to
     `brain/<topic>.md`; shows the diff (new file → whole content shown).
   - On approval, writes the brain file AND moves the original memo into
     `archive/`.
   - A later session updates one fact → shows a line-level diff that amends the
     existing line rather than appending a contradictory one.
7. [x] Confirm the archive step (original → `archive/`) is tied to the brain
   write so originals are never lost and never duplicated into the brain.

## Resolution (2026-06-01)

### Protocol confirmations (tasks 1–4, 7)

- **Four rules (task 1)** — stated and consistent across all three sources:
  `brain-protocol.md` ("Four rules for a healthy brain"), the main SKILL.md
  ("Discipline 2 — Brain"), and ARCHITECTURE §5: distill-don't-copy; always show
  a diff; no new files without asking; update existing lines. ✓
- **Layer model + no-inbox (task 2)** — `brain-protocol.md` carries the
  four-layer table (brain=permanent / log=process / output=deliverables /
  archive=originals) and "There is **no inbox folder.** Input arrives through the
  chat," matching §5. ✓
- **Cycle (task 3)** — SHARE → DISTILL (diff+approval) → LOG → USE → DELIVER →
  WRITE BACK is spelled out in "The cycle in one glance"; the project `CLAUDE.md`
  lists which brain files to read at session start (now a commented list seeded
  empty per plan 04, un-commented as brain files are created). ✓
- **File-splitting (task 4)** — start with 1–2 files, split when too large/broad;
  typical names `<topic>.md`, `landscape.md`/`overview.md`, `links.md`,
  `decisions.md`, `data-model.md`. ✓
- **Archive tie (task 7)** — distillation step 4 keeps the original in
  `archive/`, bound to the same approved write; the original is never lost and
  never duplicated into the brain (`archive/` holds the whole original; `brain/`
  holds only the essence). ✓

### "Show a diff", defined operationally (task 5)

The gatekeeper is the same approval in both cases; only the *presentation*
differs, and it stays non-technical (ARCHITECTURE §2):

- **New brain file** → the whole file IS the diff. Present it as: *"I'll create
  `brain/<file>.md` with:"* followed by the full proposed content, then ask
  Yes / Adjust / Not now. There is no "before"; the entire file is the addition.
- **Edit to an existing brain file** → a **line-level** before→after. Present
  only the changed line(s): *"I'll update this line in `brain/<file>.md`:"* then
  `before:` <old line> / `after:` <new line>, and ask. Amend the existing line —
  never append a contradictory second version (rule 4).

Presentation form (resolves the open question): use a plain **before/after
block**, not a unified `+/-` patch — non-technical users read before→after more
easily. The word "diff" never needs to appear in the chat.

### Worked example (task 6) — distill → diff → approval → write + archive

**1. User shares a strategy memo** in the chat (pasted text or an attached
file). This is the inbox — there is no separate folder.

**2. Sidekick distills 3–4 durable points** and, since `brain/` has no file on
this topic yet, proposes a **new** file (whole-file diff):

> "I'll create `brain/strategy.md` with:"
> ```markdown
> # Strategy
>
> _Last updated: 2026-06-01_
>
> - Focus FY26 on the mid-market segment; deprioritize enterprise RFPs.
> - Target 3 lighthouse customers by Q3 before broad GTM.
> - Pricing moves to annual-only to improve retention.
> - Hiring gated on closing the Series A (expected Q4).
> ```
> → Create it / Adjust / Not now

**3. On approval**, Sidekick (a) writes `brain/strategy.md`, and (b) moves the
original memo into `archive/` (e.g. `archive/20260601-strategy-memo.md`) in the
same step — original preserved, not copied into the brain. It also logs the
session freely in `log/20260601-strategy.md`.

**4. A later session updates one fact** (Series A now expected Q3, not Q4). This
is an **edit**, so a line-level before/after — amend, don't stack:

> "I'll update this line in `brain/strategy.md`:"
> `before:` - Hiring gated on closing the Series A (expected Q4).
> `after:`  - Hiring gated on closing the Series A (expected Q3).
> → Update it / Leave it

On approval, the single line is amended (no second contradictory bullet), the
`_Last updated:_` date bumped, and the change logged in `log/`.

### Open questions — decided

- **Diff presentation in Cowork** — decided above: non-technical **before/after
  block** (whole content for a new file; changed line(s) for an edit). The
  brain-protocol reference already says "show a diff"; this operational detail
  can optionally be folded into `brain-protocol.md` as a small enhancement (see
  proposed diff below) but is **not required** for correctness.
- **Archive vs connectors** — when the "shared document" actually lives in
  connected storage (Drive/OneDrive) rather than the chat, "move the original to
  `archive/`" means **keep a local snapshot copy in `archive/`** (the connector
  original may later change or disappear; the archive must be self-contained).
  Confirm with the user at the moment it happens.

### Optional proposed diff (not applied — defer to plan 13 or the 08-batch)

`brain-protocol.md` step 2 could spell out the new-file-vs-edit presentation. Low
priority; the operational rule is captured here and the protocol already mandates
"show a diff." Mark **ready, optional**.

```
- In brain-protocol.md "Step 2 — Distill", after rule 5 ("Show a diff…"), add:
  > For a brand-new brain file, the whole file is the diff (show the full
  > proposed content). For an edit, show only the changed line(s) as a plain
  > before/after — amend the existing line, never stack a second version.
```

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
