---
flowId: sidekick-checkin
nodeId: checkin-entry
type: process
slug: checkin-entry
status: current
kind: derived
summary: Entry point for the user-initiated check-in — reads settings, lists non-archived projects, gathers the latest _triage/ findings and (if connected) upcoming calendar items.
systems: [skills]
domains: [triage-checkin]
mainCodeFile: skills/sidekick-checkin/SKILL.md
entry: true
edges:
  - to: sidekick-checkin/data-backup
    via: starts
    label: back up data before walking
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Opens the cross-project check-in: load settings, enumerate the projects to walk, and pull the inbound material (triage findings + calendar) every per-project proposal is built against.
**Inputs:** trigger: user runs `/sidekick-checkin` or asks for a review / "what needs my attention"; reads `sidekick.settings.md`; lists `projects/`; reads latest `_triage/` file(s); optional calendar fetch.
**Outputs:** an in-memory worklist of non-archived projects + the freshest triage findings and near-term calendar items; hands off to data-backup.
**Code anchor:** [skills/sidekick-checkin/SKILL.md](../../../skills/sidekick-checkin/SKILL.md)
**Edges:** → sidekick-checkin/data-backup (starts)
**Key rules:**
- Gate: no `sidekick.settings.md` AND no cowork MCP tools → say this isn't a Sidekick workspace and stop.
- Walk direct children of `projects/` only; `_archive/` is skipped and `brain/<area>`/`output/<area>` subfolders are areas of their parent, not separate projects.
- Use only the latest `_triage/` file(s) since the previous check-in; missing triage is non-fatal — run from agendas + calendar.
- Calendar access is read-only.

## Functional (user facing)

### Why use this?
This is where you sit down and steer. The check-in pulls together everything that has accumulated since you last looked — what each project's agenda still has open, what the background triage flagged, and what your calendar has coming up — so you can make decisions instead of going folder by folder. This first step just gathers that picture; the proposals come right after.

### What it does
- Reads your settings first: the language to talk to you in, the output language, whether a calendar is connected, and whether output sync is on (and to which folder).
- Lists every active project, ignoring anything you have archived.
- Treats areas inside a project (a sub-topic with its own brain or output subfolder) as part of that project's walk, not as projects of their own — the parent agenda already carries their items.
- Picks up the most recent triage findings produced since your last check-in. If there are none, the check-in still runs from your agendas and calendar and simply notes there were no new findings.
- If a calendar is connected, looks ahead roughly one to two weeks for upcoming items — read-only, it never changes your calendar.

### Behind the scenes
Nothing is decided or written here. This step is pure assembly: the settings tell it how to behave, the project list tells it what to walk, and the triage and calendar give it the raw material each project's proposals will draw on. With that in hand it moves straight to backing up data before touching any project.

### Pro tips
- If a check-in feels thin, it usually means the triage hasn't run recently — the check-in only consumes what triage has already deposited in `_triage/`, it doesn't scan your inbox itself.
- A project nested as an area won't appear as its own line; look for it under its parent.

### Related
- [data-backup](data-backup.md) — the very next step, run before any project is processed.
- [per-project-walk](per-project-walk.md) — where the gathered material becomes per-project proposals.

## Technical

`skills/sidekick-checkin/SKILL.md` "Preconditions" section is the contract this node implements. The skill is prompt-only — there is no entrypoint script; the model executes the steps.

- **Gate.** The `> **Gate:**` blockquote and the description tail enforce Cowork-only operation: absent `sidekick.settings.md` and absent cowork MCP tools → the skill states it is not a Sidekick workspace and halts before any walk. This is the per-skill arm of the surface gate (ARCHITECTURE §1b).
- **Settings read.** `sidekick.settings.md` supplies chat language, output language, calendar connection, and the two sync fields (**Output sync** yes/no + **Output sync base path**) later consumed by reconcile-output-sync. Field semantics: ARCHITECTURE §8.
- **Project enumeration.** Direct children of `projects/` only; `_archive/` excluded; subprojects/areas (`brain/<area>/`, `output/<area>/`) fold into the parent walk (ARCHITECTURE §3.4). The parent's `agenda.md` already lists area items.
- **Triage intake.** Reads the latest `_triage/` file(s) since the previous check-in (ARCHITECTURE §10). Absence is tolerated; the check-in degrades to agenda+calendar.
- **Calendar intake.** When a calendar connector is configured, fetches the next ~7–14 days, read-only.

**Dependencies.** Hands off to `sidekick-checkin/data-backup` (the per-project data safeguard runs before any project body). Downstream the gathered findings flow into `sidekick-checkin/per-project-walk`. No code dependency on data.py or sync_server.py at this node — those bind to data-backup and reconcile-output-sync respectively.
