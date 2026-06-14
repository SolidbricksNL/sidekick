---
domains:
  - output-sync
edges:
  - label: runs sync.reconcile
    to: sidekick-sync/sync-engine
    via: starts
  - label: on conflict, defer to user choice
    to: sidekick-sync/resolve-output
    via: calls
flowId: sidekick-sync
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/sync_server.py
nodeId: reconcile-output
parent: main/sidekick-sync
related:
  - sidekick-checkin/reconcile-output-sync
  - session-startup/reconcile-output-sync
slug: reconcile-output
status: current
summary: The reconcile_output tool — two-way reconciles a project's output/ and artifacts/ against the external storage base path, crossing the host/Drive boundary the sandboxed shell cannot reach.
systems:
  - mcp-server
type: integration
---

## TLDR (agent)
**Purpose:** Two-way reconcile a project's `output/` and `artifacts/` with the external base path, crossing the host/Drive boundary the sandbox shell cannot reach.
**Inputs:** `project` (ABSOLUTE project dir), `base` (external base path, e.g. `G:\My Drive\sidekick`); the per-file manifest `.sidekick/sync.json` as baseline.
**Outputs:** JSON summary `{pushed, pulled, in_sync, conflicts, errors, warnings}`; changed files copied across; manifest rewritten.
**Code anchor:** [skills/sidekick-core/scripts/sync_server.py](../../../skills/sidekick-core/scripts/sync_server.py)
**Edges:** → sidekick-sync/sync-engine (starts sync.reconcile), → sidekick-sync/resolve-output (defer conflicts to user)
**Key rules:**
- Never resolves a conflict itself — it reports conflicts and the agent asks the user, then calls resolve_output.
- Additive: a one-sided delete is re-created from the surviving side, never propagated.
- Runs natively (host process), so copies reach the filesystem the storage client watches — a sandbox-shell sync silently does not.

## Functional (user facing)

### Why use this?
This is what keeps your finished work in two places at once: the project's `output/` and `artifacts/` folders inside Cowork, and the same folders on your synced Drive (or OneDrive) so you and colleagues see them where you keep files. Run it and edits flow both ways — new deliverables land in Drive, and changes someone made in Drive come back into the workspace.

### When it runs
The agent calls it automatically at three moments: right after a confirmed output write, at session start for the active project, and as a sweep at each check-in. Each call is a full two-way pass, so you rarely think about it.

### What it talks to
Your external storage folder — a mounted/synced Google Drive for Desktop or OneDrive path that you set as the Output sync base path. Under that base, each project gets its own folder mirroring its workspace `output/` and `artifacts/` trees.

### Behind the scenes
For every file it compares three things: the local copy, the external copy, and a remembered baseline. If only one side changed, that side wins and is copied over the other. If a file exists on just one side, it is copied across (sync never deletes). If both sides changed since the baseline, it does not guess — it reports a conflict and stops there, leaving your data untouched until you decide. Only `output/` and `artifacts/` are touched; your brain, logs, and data store are never synced.

### Pro tips
- The first sync has no baseline, so every file simply copies across — no false conflicts.
- A one-sided delete comes back on the next sync (it is re-created from the side that still has it); to truly remove a deliverable, delete it on both sides.
- Always pass the absolute project path — a relative path can reconcile the wrong folder.
- The return value lists exactly what was pushed, pulled, left in sync, and what conflicted, so you can see the result at a glance.

### Related
- sidekick-sync/sync-engine — the shared push/pull/conflict rule this tool runs.
- sidekick-sync/resolve-output — settles a reported conflict the way you chose.
- sidekick-sync/mcp-server — the host process that exposes this tool.

