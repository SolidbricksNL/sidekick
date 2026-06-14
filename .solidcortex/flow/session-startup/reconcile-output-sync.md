---
domains:
  - output-sync
flowId: session-startup
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/references/sync-discipline.md
nodeId: reconcile-output-sync
parent: sidekick-core/session-startup
related:
  - sidekick-sync/reconcile-output
  - sidekick-checkin/reconcile-output-sync
slug: reconcile-output-sync
status: current
summary: When output sync is enabled, call the sidekick-sync MCP reconcile_output tool with the absolute project path to two-way sync output and artifacts with external storage before work begins.
systems:
  - mcp-server
type: integration
---

## TLDR (agent)
**Purpose:** When Output sync is on, two-way sync the active project's `output/` and `artifacts/` with external storage at session start, before work begins.
**Inputs:** trigger = session start once the active project is known AND Output sync is on with a base path set; calls the `sidekick-sync` MCP tool `reconcile_output(project, base)`.
**Outputs:** `pushed`/`pulled`/`in_sync`/`conflicts`/`errors`/`warnings`; on conflicts asks the user then calls `resolve_output`; on errors reports and continues.
**Code anchor:** [skills/sidekick-core/references/sync-discipline.md](../../../skills/sidekick-core/references/sync-discipline.md)
**Edges:** ← session-startup/load-project-context (parent)
**Key rules:**
- Runs only when Output sync is on AND a base path is set; no base path → does not run.
- `project` must be the ABSOLUTE project path — a relative path resolves against the wrong dir and silently syncs nothing.
- Sync is additive — it never deletes; a one-sided delete is re-created from the surviving side.
- Conflicts always go to the user via the picker; reconcile never resolves one itself.

## Functional (user facing)

### Why use this?
If you keep your finished work on a synced drive (Google Drive for Desktop, OneDrive), this step makes a session start from the latest version of everything. Edits a colleague made in the shared folder flow in before you begin, and your deliverables and live dashboards reach the drive where everyone else can find them — without you copying files around or risking an overwrite.

### When it runs
At session start, right after Sidekick has picked the active project — but only when Output sync is turned on and a storage base path is set. With sync off, or no base path, this step simply doesn't happen.

### What it talks to
Your external storage folder — a synced drive like Google Drive for Desktop or OneDrive that the workspace can reach. Only two folders move: the project's deliverables and its generated dashboard files. Your notes, memory, and raw data never leave the workspace.

### Behind the scenes
For each file, Sidekick compares the workspace copy and the storage copy against a remembered baseline: if only one side changed, that side wins; if both changed, it stops and asks you which to keep — it never silently overwrites. Files present on only one side are copied across, so nothing is lost. If the drive can't be reached or a copy fails, Sidekick tells you what didn't sync and carries on — syncing never blocks your work.

### Pro tips
- A delete only takes effect if you remove the file on both sides — a one-sided delete comes back from the surviving copy.
- "Keep both" on a conflict preserves your version and the external one side by side, so you never lose either.
- If a sync reports a missing local folder, the project path was wrong or relative — that is the usual cause of "it synced nothing".

### Related
- session-startup/load-project-context — the parent step; the active project must be known before this reconcile runs.

## Technical

**Boundary.** This is an `integration` node: it crosses the host/external-storage boundary via the bundled **`sidekick-sync` MCP server** (`scripts/sync_server.py`, stdlib Python, declared in `.claude-plugin/plugin.json` under `mcpServers`). A plugin MCP server runs as a native host process, so its binary-safe file copies land on the real filesystem the storage client watches and sync actually fires — unlike a bash-sandbox copy (which writes to a Linux mountpoint the client never notices) or a connector upload (which would make the model base64 the file into its own output). Backing protocol: `skills/sidekick-core/references/sync-discipline.md`; design in `docs/ARCHITECTURE.md` §7c.

**Tool call.** `reconcile_output(project, base)` — `project` is the ABSOLUTE project dir (`<workspace root>/projects/<slug>`, workspace root = the dir holding `sidekick.settings.md`); `base` is the Output sync base path from settings. Two-way syncs `<project>/{output,artifacts}/` ↔ `<base>/<slug>/{output,artifacts}/`. A relative `project` resolves against the wrong directory (a Cowork scratchpad) and silently syncs nothing — a `warnings` entry about a missing local dir signals exactly that. Runtime tool name is host-namespaced (`mcp__sidekick-sync__reconcile_output`); CLI equivalent `sync.py reconcile`.

**Result handling.** Returns `pushed`, `pulled`, `in_sync`, `conflicts`, `errors`, `warnings`. On `conflicts`, ask the user per file via the picker (keep local / external / both) then call `resolve_output(project, base, file, keep)` with `keep ∈ local|external|both` (`both` keeps the local file and the external one as `<name>.from-external<ext>` on both sides). On `errors`/unreachable base, report and continue — never block a local write.

**Reconcile rule (per file).** Manifest `projects/<slug>/.sidekick/sync.json` (path → last-synced content hash; in hidden `.sidekick/`, never inside `output/`/`artifacts/`, so it is never itself synced) holds the baseline. Same content → in sync; one side changed → copy that side over; both changed (or no baseline, differing) → conflict, left untouched and reported; file on one side only → copied (additive); gone on both → dropped. First sync (no manifest) copies everything with no false conflicts. Performance: `reconcile` hashes both sides, so the first run against a large "files-on-demand" store is slower (hashing may pull files down).

**Fallback / deploy.** If the `sidekick-sync` tools are unavailable (server didn't start — Python must be on host PATH, else set an absolute interpreter in the manifest `command`), fall back to the `sync.py` CLI and warn the user that a sandboxed copy may not reach the storage client.

**Dependencies.** Parent `session-startup/load-project-context` (active project must be selected first). Same `reconcile_output` call also fires after a confirmed output write and at the check-in sweep (§7c); those moments live in other flows.
