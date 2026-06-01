# Write-disciplines enforcement

**Status:** done (gatekeeper matrix complete; 1 tightening = Diff A, owned by plan 08)
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
1. [x] Restate the decision rule crisply (from `write-disciplines.md`) and
   confirm it matches ARCHITECTURE §2 exactly (including the 3b database row and
   the "records that fit are free" carve-out).
2. [x] Enumerate **every write action** each skill performs or proposes:
   - `sidekick`: log files, brain distillation, output deliverables, sqlite
     structure + records, agenda updates, project scaffolding.
   - `sidekick-init`: settings file, first-project scaffold, root system folders.
   - `sidekick-triage`: ONLY `_triage/YYYYMMDD-triage.md` (nothing else).
   - `sidekick-checkin`: brain (via approval), output (via confirm), agenda
     (free bookkeeping), reply drafts (no send without explicit ok), log of what
     it processed.
   - `sidekick-archive`: move project folder; no other writes; never deletes.
3. [x] Build the **gatekeeper matrix**: rows = write actions, columns = {target
   location, gatekeeper required, where stated in the skill, ARCHITECTURE ref}.
4. [x] Flag every cell where a skill could write without the right gatekeeper,
   or where the wording is ambiguous about which gatekeeper applies. Capture
   each as a proposed wording fix (defer application; coordinate with plan 02).
5. [x] Special checks:
   - Agenda writes are classified as free bookkeeping (log-like), not gated —
     confirm this is intended and stated consistently (checkin says so).
   - Settings file write (init) — classify its gatekeeper (it's a confirmed
     write after summary; document it).
   - Triage writing ONLY to `_triage/` — confirm nothing in its body permits any
     other write.
6. [x] Confirm the "log to disk, summarize in chat — never the reverse" rule is
   present wherever substantive output could otherwise leak into chat.

## Resolution (2026-06-01)

### Decision rule (task 1) — matches §2

`write-disciplines.md` restates the rule and matches ARCHITECTURE §2 exactly:
`log/` = free; `brain/` = diff + approval; `output/` = confirm create/edit/delete;
`data.sqlite` **structure** = confirm in plain language; `data.sqlite` **record
that fits** = free. The 3b database row and the "records that fit are free"
carve-out are both present and worded consistently across §2, §4, and the
reference. ✓

### Gatekeeper matrix (task 2, 3) — every write action, all five skills

| Skill | Write action | Target | Gatekeeper | Stated where | ARCH |
|---|---|---|---|---|---|
| `sidekick` | session/topic log | `log/YYYYMMDD-<slug>.md` | **free** | "Discipline 1 — Log freely" | §6 |
| `sidekick` | brain distillation | `brain/*.md` | **diff + approval** | "Discipline 2" | §5 |
| `sidekick` | deliverable | `output/*` | **confirm** create/edit/delete | "Discipline 3" | §7 |
| `sidekick` | schema change | `data.sqlite` | **confirm** (plain language) | "Discipline 3 / database" | §4 |
| `sidekick` | record that fits | `data.sqlite` | **free** | "Populating existing tables… is free" | §4 |
| `sidekick` | agenda update | `agenda.md` | **free** (bookkeeping) | implied; explicit in checkin | §11 |
| `sidekick` | project scaffold | `projects/<slug>/…` | **confirmed** (explicit approval; never silent) | "Project detection" / "Never silently create" | §3.0–3.1 |
| `sidekick-init` | settings file | `sidekick.settings.md` | **confirmed** (after summary) | "summarize all answers and ask for confirmation before writing" | §8 |
| `sidekick-init` | first-project scaffold | `projects/<slug>/…` | **confirmed** (user named project) | "Scaffolding the first project" | §3.0 |
| `sidekick-init` | root system folders | `_triage/`, `_archive/projects/` | **confirmed** (part of setup) | step 3 of scaffolding | §3 |
| `sidekick-triage` | findings file | `_triage/YYYYMMDD-triage.md` | **free, but the ONLY allowed write** | "Write only to `_triage/`" | §10 |
| `sidekick-checkin` | brain update | `brain/*.md` | **diff + approval** | "Acting on approvals → Brain" | §5 |
| `sidekick-checkin` | deliverable | `output/*` | **confirm** | "Acting on approvals → Output" | §7 |
| `sidekick-checkin` | schema change | `data.sqlite` | **confirm** (plain language) | "Output/database structure" | §4 |
| `sidekick-checkin` | agenda update | `agenda.md` | **free** (bookkeeping) | "update agenda.md directly… written freely like the log" | §11 |
| `sidekick-checkin` | reply | external (email/chat) | **draft only**; send needs explicit ok | "Reply — Draft only… never send unprompted" | §11 |
| `sidekick-checkin` | check-in log | `log/YYYYMMDD-checkin.md` | **free** | "Log it… freely" | §6 |
| `sidekick-archive` | move project | `projects/<slug>/` → `_archive/projects/<slug>/` | **confirmed** (explicit yes); **never deletes** | "Confirm" + "Boundaries" | §3.3 |

### Flagged cells (task 4) — gating gaps

Exactly **one** tightening, already raised in plan 02 and owned downstream:

- **Triage's single allowed write.** The boundary "Write only to `_triage/`" is
  correct, but the enumerated negatives can be read as a closed list of only
  project files. → **plan 02 Diff A** makes `_triage/`-only exhaustive (apply in
  plan 08). No new diff here.

No other cell is mis-gated or un-gated. Every gated write routes through the
correct gatekeeper; every free write is intentionally free (see below).

### Special checks (task 5, 6)

- **Agenda classification (open question — decided).** `agenda.md` is a
  **lightweight free-write bookkeeping** category, sibling to the log, **not** a
  gated discipline. It is user-facing but is just a live status list the check-in
  consumes. The checkin skill states this ("written freely like the log"); the
  main skill and §2's three-row table don't list it. Decision: keep it free;
  **clarify §2** to name agenda as a free bookkeeping write at the plan-13 docs
  pass (already tracked as plan 02 contradiction-table #3). No skill diff needed.
- **Settings + scaffold writes (decided).** Init's `sidekick.settings.md` write
  and first-project scaffold are **confirmed one-time setup writes** done after an
  explicit summary+confirm — they do **not** need the brain-style diff. Correctly
  classified as "confirmed," not "diff + approval."
- **Triage `_triage/`-only.** Re-read the full triage body: no clause anywhere
  permits a write outside `_triage/`. The hard-boundaries section forbids all
  other targets; Diff A only closes the read-as-exhaustive wording risk. ✓
- **Chat-leak rule (task 6).** "Log to disk, summarize in chat — never the
  reverse" is present in `write-disciplines.md` ("Always log to disk and
  summarize in the chat — never the reverse") and in the `sidekick` skill
  ("Log to disk, summarize in chat"). It is a **behavior, not a file boundary**,
  so it can only be confirmed by the manual walkthroughs (plan 12), not by a
  script.

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
