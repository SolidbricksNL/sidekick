---
domains:
  - reporting
flowId: sidekick-sync
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/reports.py
nodeId: save-report
parent: main/sidekick-sync
related:
  - sidekick-report/save-report-recipe
slug: save-report
status: current
summary: The save_report tool — registers or merges an entry in the project's .sidekick/reports.json recipe registry, validating the name and writing either a query recipe (named SELECT) or a sql-less dashboard registration.
systems:
  - mcp-server
type: process
---

## TLDR (agent)
**Purpose:** Register or merge one entry in the project's `.sidekick/reports.json` recipe registry — either a query recipe (a named `SELECT`) or a sql-less dashboard registration.
**Inputs:** `project` (ABSOLUTE), `name` (slug-ish), and any of `sql`, `desc`, `artifact`, `drive_file_id`, `tables`.
**Outputs:** Merged entry persisted to `.sidekick/reports.json`; JSON `{ok, action:"save", report, entry}`.
**Code anchor:** [skills/sidekick-core/scripts/reports.py](../../../skills/sidekick-core/scripts/reports.py)
**Edges:** (none)
**Key rules:**
- An entry is EITHER a query recipe (`sql`) OR a dashboard registration (`artifact`+`drive_file_id`+`tables`) — a multi-sub-query report is one recipe per sub-query, not one with a representative sql.
- The name must match `^[A-Za-z0-9][A-Za-z0-9_-]*$`; a brand-new entry needs at least `sql` OR `artifact`/`drive_file_id`.
- Merges field-by-field — only given fields update — so `drive_file_id` can be set later without resending `sql`.

## Functional (user facing)

### Why use this?
This is Sidekick's memory for reports. Once you have asked for something — say the monthly revenue breakdown — it can be saved as a named recipe so the same answer is one word away next time, never re-derived from scratch. It also records the dashboards a project has produced, so the project knows what it has and what to refresh when the data changes.

### What it does
- Saves a named report recipe: a plain description plus the exact read-only query that produces it.
- Alternatively registers a produced dashboard (its file, its Drive id, and the data tables it reads) so the project can find and refresh it later.
- Remembers which data tables each recipe reads, so when those tables change Sidekick knows exactly which reports to regenerate.
- Merges updates into an existing entry, so you can fill in a detail (like the Drive id) later without re-supplying everything.

### Behind the scenes
The registry is a machine-readable file kept in the project's hidden state folder; the human-readable version of each report lives in the brain and is approved like any other project knowledge. A report with several named sub-views is stored as one recipe per sub-view rather than squeezed into a single representative query — so each view stays exact and runnable. Saving runs natively so the file is written reliably; hand-writing it or shelling out can truncate on the sandbox mount.

### When it runs
Whenever a new report recipe is approved, or a dashboard is produced and its Drive file becomes known. Saving a recipe is a brain write, so it goes through the usual approval before it is recorded.

### Pro tips
- Give recipes clear slug-ish names (letters, digits, underscore, hyphen) — that name is how they are run later.
- You do not need everything at once: save the query now, add the Drive id after the dashboard syncs.
- Listing the data tables a recipe reads is what lets a data change auto-refresh the right reports — worth filling in.

### Related
- sidekick-sync/build-dashboard — bakes a dashboard whose tiles can bind to a saved recipe by name.
- sidekick-sync/mcp-server — the host process that exposes this tool.

