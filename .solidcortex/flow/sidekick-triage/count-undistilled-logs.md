---
flowId: sidekick-triage
nodeId: count-undistilled-logs
type: process
slug: count-undistilled-logs
status: current
kind: derived
summary: Read each non-archived project's log/ folder and count the log files lacking the distilled-to-brain stamp, producing a one-line per-project heads-up count without listing individual logs.
systems: [skills]
domains: [triage-checkin]
parent: main/sidekick-triage
mainCodeFile: skills/sidekick-triage/SKILL.md
edges:
  - to: sidekick-triage/write-findings-file
    via: starts
    label: contribute per-project log counts
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Count each non-archived project's undistilled log files and emit a one-line per-project heads-up number.
**Inputs:** Each non-archived `projects/<slug>/log/*.md` file; the `> distilled to brain:` footer stamp.
**Outputs:** One "Undistilled logs: N" line per project, handed to write-findings-file.
**Code anchor:** [skills/sidekick-triage/SKILL.md](../../../skills/sidekick-triage/SKILL.md)
**Edges:** ← sidekick-triage/compute-scan-window (parent), → sidekick-triage/write-findings-file (starts)
**Key rules:**
- Count only — never list, analyse, or create per-log findings; never write to `brain/` or `log/`.
- A log counts as undistilled when it lacks the `> distilled to brain:` footer stamp.
- Skip any log modified within the last hour (still being written).
- It is a fresh snapshot regenerated every run; the check-in does the actual distilling.

## Functional (user facing)

### Why use this?
This gives you a per-project heads-up of how many work logs are still waiting to be folded into the project's long-term memory — a quick "you have a backlog here" signal — without triage touching that memory itself.

### What it does
- Looks inside each of your active projects' log folders.
- Counts the log entries that have not yet been distilled into the project's brain.
- Reports just a number per project, like "Undistilled logs: 2".
- Leaves out logs you wrote in the last hour, since those are probably still in progress.
- Ignores archived projects entirely.

### Why only a count?
Triage deliberately does not list or summarise the individual logs and never creates a finding per log. If it did, the same un-actioned log would resurface as a finding on every single run and clutter your findings. Instead, the count is a plain snapshot, recomputed from scratch each time. The actual work of reading those logs and distilling them into the brain happens during the check-in, which also stamps each log as done so it stops being counted.

### Pro tips
- A rising count across runs means logs are piling up — a nudge to run a check-in soon.
- Editing a log resets nothing; only the check-in's distill-and-stamp step removes it from the count.

### Related
- [compute-scan-window](compute-scan-window.md) — the run that launches this count.
- [write-findings-file](write-findings-file.md) — places each count under its project heading.

## Technical

Instruction-only; implemented in the "Note undistilled-log counts" section of `skills/sidekick-triage/SKILL.md`. No compiled code.

- Trigger: dispatched by `compute-scan-window` alongside the source scans. Independent of the scan window cutoff (it is a current-state snapshot, not a time-bounded diff).
- Algorithm: for each direct child of `projects/` that is non-archived, enumerate `log/*.md` and count files missing the `> distilled to brain:` footer stamp. Exclude any log modified within the last hour. Emit one `Undistilled logs: N` line per project; in the findings file it renders as `_Undistilled logs: {{N}}_` under the project heading (see triage-template.md).
- Constraints (SKILL.md "Hard boundaries" + this section): pure read; never lists or analyses individual logs, never creates per-log findings, never writes to `brain/` or `log/`. This is what prevents an un-actioned log from recurring as a finding across runs.
- Division of labour: counting here is informational; the check-in (`sidekick-checkin`) is what scans `log/` itself, distills each undistilled log into the brain on approval, and writes the `> distilled to brain: <date>` stamp. See ARCHITECTURE.md §10 step 2 and §11 steps 4-7. The same stamp drives `sidekick-status`'s undistilled-log count.
