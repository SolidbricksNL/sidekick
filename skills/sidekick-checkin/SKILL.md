---
name: sidekick-checkin
description: User-initiated cross-project review. Use when the user runs /sidekick-checkin or asks for a check-in, a review of where things stand, "what needs my attention", or to go through the triage findings. Walks every non-archived project, reads each agenda.md, cross-references the latest triage findings in _triage/ and — if connected — the calendar, and proposes concrete actions per project. All proposed changes follow the normal gatekeeper rules: brain changes need a diff + approval; output and database-structure changes need confirmation. Cowork Sidekick workspaces only — without sidekick.settings.md and outside Cowork, reply that this is not a Sidekick workspace and stop.
---

# Sidekick — Check-in

> **Gate:** no `sidekick.settings.md` and no cowork MCP tools (Claude Code /
> code repo / plain chat)? Say this isn't a Sidekick workspace and stop.

You run the user's cross-project check-in. You bring together what each
project's agenda says, what the triage found, and what the calendar
shows, and you turn that into a short, decision-ready set of proposals.
You are the moment where triage suggestions become real actions — but
only with the user's go-ahead, item by item.

**Present proposals through the interactive question prompt — not as text
cards.** Each proposal is one question (options like Yes / No / Edit / Skip),
raised via Cowork's tappable picker, **up to 4 per prompt**, then loop for the
next batch. Do **not** write the proposals into the chat as a list of
styled cards or "buttons" — text you format yourself is **not clickable**,
however nice it looks; the only tappable control is the question prompt
itself. This is the plugin-wide interaction style — see
`../sidekick-core/references/interaction-style.md`.

## Preconditions

1. Read `sidekick.settings.md` (chat language, output language,
   connected calendar, **Output sync + Output sync base path**).
2. List `projects/` (non-archived only — ignore `_archive/`). **Direct
   children only:** a project's `brain/<area>/` or `output/<area>/` subfolders
   are subprojects/areas, handled as part of the parent walk — not separate
   projects. The parent's `agenda.md` already carries the area's items.
3. Read the **latest** `_triage/` file(s) since the previous check-in. If
   there is none, the check-in still runs from agendas and calendar; just
   note that there are no new triage findings.
4. If a calendar is connected, fetch upcoming items in the near term
   (e.g. next 7–14 days). Read-only.

## Per-project walk

For **each** non-archived project, in a sensible order (e.g. most
recently active first):

0. **Back up structured data first.** If the project has a `data/` folder,
   run a timestamped backup **before doing anything else** with it. Resolve the
   helper (`$CLAUDE_PLUGIN_ROOT` is unset in the shell):
   `SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`, then
   `python3 "$SK/data.py" backup --project projects/<slug> --label check-in`
   (writes a dated copy into `data/.backups/`). This is a hard rule — the
   check-in never processes a project's data without first taking a dated
   backup. Skip silently for projects that have no `data/` yet.
1. Read the project's `agenda.md` (open items, waiting-on, notes for next
   check-in) and the brain index from its `CLAUDE.md` for context.
2. Pull any triage findings tagged to this project.
3. Pull any calendar items related to this project (by topic/people).
4. **Scan the project's `log/` for undistilled logs** — files lacking the
   `> distilled to brain:` stamp (skip a log modified within the last hour,
   still being written). This is the check-in's own scan; the triage only
   reports a count, so the check-in is the single place that detects and
   processes them.
5. Synthesize: what's moved, what's stuck, what's new, what's due.
6. Propose **concrete actions**, each tagged with its type and its
   gatekeeper:
   - **Update brain** — durable fact/decision → will show a diff and need
     approval.
   - **Distill a log** — an undistilled `log/` file found in step 4 whose
     insights belong in the brain → show a diff and need approval, then
     stamp the log (see "Acting on approvals").
   - **Do an action** — a task to perform now in this session.
   - **Create a deliverable** — something in `output/` → needs
     confirmation; generated in the default output language.
   - **Structured data** — load/correct records via `scripts/data.py`; a
     new table or column needs plain-language confirmation first.
   - **Reply** — to an email or chat. **Draft only** unless the user
     explicitly approves sending; never send unprompted.
   - **Agenda** — add a new item, or tick/close an existing one.
   - **Calendar** — note a commitment (read-only; you don't modify the
     calendar).

Raise each project's proposals through the question prompt (≤4 per prompt,
then loop) so the user taps yes/no/edit per item — never a rendered card
list. A short prose summary of what you found is fine; the *decisions* go
through the picker.

## Handling "new project?" findings

For triage items in the "Unassigned / new project?" group, present them
together and ask whether to start a new project (then hand off to the
normal scaffolding, exactly as the `sidekick` skill does) or attach them
to an existing one — or ignore them.

## Acting on approvals

Once the user approves items, carry them out under the normal
disciplines:

- **Brain:** show the diff, write after approval, move any processed
  source into `archive/`.
- **Distilled logs:** for an undistilled log found in the per-project scan,
  show the brain diff and write after approval, then **append
  `> distilled to brain: <today>` to that `log/` file** so it is not
  re-detected. If the user defers a log, leave it unstamped — it resurfaces
  at the next check-in. (The original log stays in `log/`; only the stamp is
  added.)
- **Output:** confirm, then create/edit; record what was produced.
- **Reconcile output sync — both directions** (only if Output sync is on
  **and** an Output sync base path is set): for each project call the
  **`reconcile_output`** tool from the bundled `sidekick-sync` MCP server,
  passing the **absolute** project path (`<workspace root>/projects/<slug>` —
  a relative path resolves wrong in the server and silently syncs nothing) and
  `base: "<base path>"`. It **pulls** external
  edits in and **pushes** local ones out via native file copies (**additive** —
  a deleted file is never propagated; **never** base64 a file through
  yourself), reporting `pushed`/`pulled`/`conflicts`/`errors`. For each path in
  `conflicts`, **ask via the picker** (keep Cowork / keep external / keep both)
  and call `resolve_output` — never silently overwrite. This runs whether or
  not new output was approved this check-in. A failed step / unreachable base
  path is reported, not fatal; skip silently when sync is off or no base path
  is set. (Spec: `../sidekick-core/references/sync-discipline.md`,
  ARCHITECTURE §7c.)
- **Structured data:** records that fit existing columns flow in freely via
  `scripts/data.py`; a new table or column is a structure change — confirm
  in plain language first, then update `brain/data-model.md`.
- **Agenda:** update `agenda.md` directly (this is bookkeeping, written
  freely like the log).
- **Replies:** draft in the relevant language; only send if the user
  said so explicitly in this chat.
- **Log it:** record what the check-in processed and decided in the
  relevant project's `log/` (`YYYYMMDD-checkin.md`), freely.

## Closing

Give a short wrap-up in the chat language: per project, what was decided
and what's still open; and any cross-project flags (e.g. a deadline
cluster, or a project that's gone quiet). Update each touched project's
`agenda.md` so the next check-in starts clean.

Do not turn the wrap-up into a wall of text — it's a steering summary;
the detail lives in the logs and agendas.
