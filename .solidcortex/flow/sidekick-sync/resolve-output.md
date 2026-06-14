---
flowId: sidekick-sync
nodeId: resolve-output
type: integration
slug: resolve-output
status: current
kind: derived
summary: The resolve_output tool — settles one output-sync conflict the user chose (keep local, external, or both), copying the surviving file across the host/Drive boundary and updating the manifest.
systems: [mcp-server]
domains: [output-sync]
parent: main/sidekick-sync
mainCodeFile: skills/sidekick-core/scripts/sync_server.py
edges:
  - to: sidekick-sync/sync-engine
    via: starts
    label: runs sync.resolve
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Settle one output-sync conflict the user chose — keep the local file, the external file, or both — and update the manifest baseline.
**Inputs:** `project` (ABSOLUTE), `base`, `file` (conflicting manifest key `<sub>/<relpath>`), `keep` ∈ `local|external|both`.
**Outputs:** JSON `{ok, action:"resolve", project, file, keep}`; the surviving file copied across both sides; manifest rewritten.
**Code anchor:** [skills/sidekick-core/scripts/sync_server.py](../../../skills/sidekick-core/scripts/sync_server.py)
**Edges:** → sidekick-sync/sync-engine (runs sync.resolve)
**Key rules:**
- Called only after the user picks an option in the conflict picker — it never decides on its own.
- `both` keeps the local file under its original name and the external one as `<name>.from-external<ext>` on both sides.
- Raises if the chosen side's file is missing (a stale conflict), rather than writing an empty result.

## Functional (user facing)

### Why use this?
When a two-way sync finds the same file changed on both sides, it stops and asks you rather than guessing. This is the step that carries out your answer: keep the Cowork version, keep the version on Drive, or keep both. It is the one moment in syncing where you are in control.

### When it runs
Only right after a reconcile reports a conflict and you have chosen what to do in the picker. It handles exactly one file per call — the agent calls it once for each conflict you resolved.

### What it talks to
The same external storage folder as the sync itself — your mounted Drive or OneDrive base path. It copies the surviving file across both the workspace and the Drive side so the two are back in step.

### Behind the scenes
"Keep local" copies the Cowork file out to Drive. "Keep external" pulls the Drive file back into the workspace. "Keep both" preserves your Cowork file under its original name and saves the external one beside it with a `.from-external` tag, on both sides, so nothing is lost. Whatever you chose, the remembered baseline is updated so the next sync sees the file as settled and won't flag it again.

### Pro tips
- If the file you chose to keep has since been deleted on that side, the tool reports it clearly instead of silently doing nothing — re-run the sync to refresh the conflict list.
- "Keep both" is the safe default when you are unsure: you never lose either version.
- Pass the same absolute project and base path you used for the reconcile.

### Related
- sidekick-sync/reconcile-output — the two-way sync that reports the conflict this tool settles.
- sidekick-sync/sync-engine — the shared copy/manifest logic underneath.
- sidekick-sync/mcp-server — the host process that exposes this tool.

