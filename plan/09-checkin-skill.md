# Check-in skill

**Status:** done (scripted walkthrough written; freshness + calendar decided)
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
1. [x] Confirm preconditions: read settings (chat lang, output lang, connected
   calendar); list non-archived `projects/`; read latest `_triage/` file(s) since
   the previous check-in (and proceed gracefully if none); read near-term
   calendar if connected (read-only).
2. [x] Confirm the per-project walk: read `agenda.md` + brain index; pull triage
   findings tagged to the project; pull related calendar items; synthesize
   moved/stuck/new/due; propose concrete actions, each tagged with type +
   gatekeeper (update brain / do action / create deliverable / reply draft /
   agenda / calendar-note).
3. [x] Confirm proposals are presented as quick multiple-choice (Yes / No / Edit
   first) so the user can run through them by tapping (ties to plan 11).
4. [x] Confirm the "Unassigned / new project?" handling: present together; offer
   start-new-project (hand off to canonical scaffolding) / attach-to-existing /
   ignore.
5. [x] Confirm acting-on-approvals routes correctly:
   - Brain → show diff, write after approval, move processed source to
     `archive/`.
   - Output / database structure → confirm, then create/edit; record output.
   - Agenda → update directly (free bookkeeping).
   - Replies → draft in the right language; send ONLY if the user explicitly said
     so in this chat; never send unprompted.
   - Log → record what the check-in processed in the project's `log/`
     (`YYYYMMDD-checkin.md`), freely.
6. [x] Confirm the closing wrap-up is a short steering summary (per-project
   decided/open + cross-project flags) and that each touched `agenda.md` is left
   clean for next time — not a wall of text.
7. [x] **Build the scripted walkthrough** (write it into this plan as the
   artifact): a 2–3 project sandbox with a sample `_triage/` file, run the
   check-in, show the multiple-choice proposals, simulate the user's
   approvals/declines, and show exactly which writes happen and through which
   gatekeeper, plus the resulting `log/` and `agenda.md` updates.

## Resolution (2026-06-01)

### Confirmations (tasks 1–6)

- **Preconditions (task 1)** — reads settings (chat/output lang, connected
  calendar); lists non-archived `projects/`; reads the latest `_triage/` file(s)
  since the previous check-in (proceeds gracefully if none); reads near-term
  calendar read-only if connected. ✓
- **Per-project walk (task 2)** — agenda + brain index → triage findings for the
  project → related calendar items → synthesize moved/stuck/new/due → propose
  concrete actions, each tagged with type + gatekeeper. ✓
- **Multiple-choice proposals (task 3)** — Yes / No / Edit first per item,
  tappable; ties to plan 11. ✓
- **Unassigned handling (task 4)** — present together; offer start-new-project
  (hand to canonical scaffolding) / attach-to-existing / ignore. ✓
- **Acting on approvals (task 5)** — brain (diff+approval, move source to
  `archive/`); output/db (confirm); agenda (free); replies (draft only, send
  only on explicit in-chat yes); log to `log/YYYYMMDD-checkin.md` (free). ✓
- **Wrap-up (task 6)** — short per-project decided/open + cross-project flags;
  each touched `agenda.md` left clean; not a wall of text. ✓

### Open questions — decided

- **Triage freshness.** The check-in processes **all `_triage/` files dated after
  the most recent check-in** (newer than the latest `YYYYMMDD-checkin.md` in any
  project `log/`), merged and **deduped by source identifier** so nothing is
  missed or double-counted. If it cannot determine what was already processed, it
  falls back to the single newest `_triage/` file and says so.
- **Calendar correlation.** Matching a calendar item to a project is a
  **best-effort heuristic** (shared topic/people); surfaced for the user to
  confirm, never auto-attached.
- **Reply sending (already resolved, gated).** Draft only; send only after an
  explicit in-chat "send it" via a user-enabled connector; otherwise the draft is
  left in chat or `output/` for manual sending.

### Scripted walkthrough (task 7) — the acceptance artifact

**Sandbox:** two non-archived projects — `core-roadmap`, `client-bpd` — plus the
unassigned `q4-keynote` item. Input: the unit-08 sample
`_triage/20260601-triage.md`. Calendar connected.

**Check-in opens:** reads settings (chat=EN, output=EN), lists the two projects,
loads `_triage/20260601-triage.md` (4 findings), notes no check-in log newer than
it → all four are fresh.

**— Project: core-roadmap —** (agenda open item: "decide pricing model")

> 1. **Update brain** — record the decision "FY26 = mid-market pivot" once you
>    sign off? *(brain → I'll show a diff)* → **Yes / No / Edit first**
> 2. **Reply (draft)** to Priya Shah re: sign-off? *(draft only; I won't send)*
>    → **Draft it / Skip**
> 3. **Agenda** — before Wed's "Roadmap review", tick "decide pricing model"?
>    → **Yes / No**

Simulated user: **1 → Yes**, **2 → Draft it**, **3 → No (decide live Wed)**.

Writes that happen, each correctly gated:
- (1) brain **diff shown**, approved → append to `brain/strategy.md` ("FY26:
  mid-market pivot confirmed 2026-06-01"); original triage finding referenced.
  *Brain = diff + approval.* ✓
- (2) reply **drafted** in EN to `output/` (or shown in chat) — **not sent**
  (no explicit send). *Reply = draft only.* ✓
- (3) no agenda change (declined). ✓

**— Project: client-bpd —** (agenda: "await renewal terms")

> 1. **Update brain** — add "BPD renewal window opens 2026-06; new liability
>    clause" to the brain? → **Yes / No / Edit first**
> 2. **Create deliverable** — a one-page renewal-terms summary in `output/`?
>    *(confirm before I create it)* → **Create it / Not now**

Simulated user: **1 → Edit first** (rewords the clause note), **2 → Create it**.

- (1) brain diff shown with the user's edit, approved → `brain/bpd.md` updated;
  the renewal email moved to `archive/`. *Brain = diff + approval + archive.* ✓
- (2) confirmed → `output/20260601-bpd-renewal-summary.md` created in EN.
  *Output = confirmation.* ✓

**— Unassigned / new project? —**

> "Speaker invite: Q4 keynote" doesn't match a project. Start a new project,
> attach to an existing one, or ignore? → **New project "q4-keynote" / Attach /
> Ignore**

Simulated user: **New project** → hands off to canonical scaffolding (plan 04):
creates `projects/q4-keynote/` (CLAUDE.md, agenda.md, empty brain/log/archive/
output). *Scaffold = confirmed; never silent.* ✓

**Logging (free).** Each project gets `log/20260601-checkin.md` recording what
was proposed, approved/declined, and written — no permission needed.

**Wrap-up (steering summary):**
> - **core-roadmap:** pricing decision deferred to Wed's review; mid-market
>   pivot recorded; reply to Priya drafted (unsent).
> - **client-bpd:** renewal terms captured; one-page summary created.
> - **New:** `q4-keynote` project started from the keynote invite.
> - **Flag:** Wed 10:00 review has an open pricing decision — prep it.

Each touched `agenda.md` updated (core-roadmap notes "pricing → decide Wed";
client-bpd moves "await renewal terms" → Recently done) so the next check-in
starts clean.

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
