---
flowId: sidekick-triage
nodeId: write-findings-file
type: process
slug: write-findings-file
status: current
kind: derived
summary: Write the timestamped _triage/YYYYMMDD-HHMM-triage.md findings file from the template, grouping suggestions by project with an unassigned group last, never writing to any project brain or log.
systems: [skills]
domains: [triage-checkin]
parent: main/sidekick-triage
mainCodeFile: skills/sidekick-triage/references/triage-template.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Assemble all scan results and log counts into one timestamped `_triage/` findings file from the template.
**Inputs:** Findings from scan-email/scan-chat/scan-calendar; per-project counts from count-undistilled-logs; the run timestamp; the triage template.
**Outputs:** One `_triage/YYYYMMDD-HHMM-triage.md` file (grouped by project, unassigned group last); optional one-paragraph chat summary.
**Code anchor:** [skills/sidekick-triage/references/triage-template.md](../../../skills/sidekick-triage/references/triage-template.md)
**Edges:** ← sidekick-triage/compute-scan-window (parent)
**Key rules:**
- Write ONLY to `_triage/` — never to any project brain, log, output, data, agenda, or settings; no deletions anywhere.
- One timestamped file per run; never edit a previous run's file (so triage can run several times a day).
- Group findings by suggested project; an "Unassigned / new project?" group goes last.
- Record the run time in the `_Run at:_` line; headings in the chat language, quoted snippets in their original language.

## Functional (user facing)

### Why use this?
This is where everything triage found becomes a single, readable findings file you can act on later — organised by project so you can see at a glance what is waiting on each one. It is the actual output of a triage run.

### What it does
- Creates one findings file per run, named with the date and time it ran.
- Groups every finding under the project it most likely belongs to.
- Puts items that do not match any project in an "Unassigned / new project?" group at the end.
- Adds each project's undistilled-log count as a heads-up line.
- Records when the run happened and which sources were scanned, and ends with a short summary.

### Why a new file each time
A triage run never edits an earlier run's file. Each run writes its own dated-and-timed snapshot, so you can run triage several times a day and keep a clean history — nothing overwrites anything. The later check-in reads every triage file written since you last checked in, so multiple runs in a day all get picked up.

### Where it writes
Strictly into the `_triage/` folder at your workspace root — and nowhere else. Triage never touches a project's brain, logs, outputs, data, or agenda; those are only changed during the check-in, with you present. Everything in the findings file is a suggestion that has not been acted on.

### Pro tips
- Findings are grouped by project, so during the check-in you can work through one project's items at a time.
- If you ran triage interactively, you also get a one-paragraph chat summary pointing you to the file; the file itself is the real output.

### Related
- [scan-email](scan-email.md), [scan-chat](scan-chat.md), [scan-calendar](scan-calendar.md) — the source findings collected here.
- [count-undistilled-logs](count-undistilled-logs.md) — supplies the per-project heads-up counts.
- [compute-scan-window](compute-scan-window.md) — the run that started this whole sequence.

## Technical

Backed by the layout template `skills/sidekick-triage/references/triage-template.md`; the writing rules live in the "Writing the findings file" and "Closing" sections of `skills/sidekick-triage/SKILL.md`. Instruction-only — the agent renders the template.

- Trigger: terminal step of the run; consumes the outputs of all three source scans plus `count-undistilled-logs`. It is the convergence point of the subflow's fan-out.
- File: `_triage/YYYYMMDD-HHMM-triage.md` at the Cowork root — timestamped (date + time) per run so concurrent-day runs never collide; previous run files are never edited.
- Template fields (triage-template.md): `{{DATE}}`, `_Run at:_ {{TIMESTAMP}}`, `_Scanned sources:_`, `_Window: since {{LAST_RUN_OR_WINDOW}}_`, per-project sections with `_Undistilled logs: {{N}}_`, per-finding blocks (source + short id / why-it-matters / suggested action / optional quoted-snippet notes), a trailing `## Unassigned / new project?` group, and a `## Summary`.
- Hard boundary (SKILL.md "Hard boundaries"): the ONLY writable location is `_triage/`. No writes to any `brain/`, `log/`, `output/`, `data/`, `agenda.md`, `sidekick.settings.md`, or other skills' space; no deletions. This is what keeps scheduled, unattended runs safe and the human the gatekeeper.
- Closing behaviour (SKILL.md "Closing"): when run interactively via `/sidekick-triage`, emit a one-paragraph chat summary; any offered choice (e.g. "Run the check-in now?") uses the multiple-choice picker from `sidekick-core/references/interaction-style.md`. Downstream, the file is input for `sidekick-checkin`. See ARCHITECTURE.md §10 steps 3-4.
