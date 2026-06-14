---
domains:
  - output-sync
edges:
  - label: close out the check-in
    to: sidekick-checkin/checkin-close
    via: starts
flowId: sidekick-checkin
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/scripts/sync_server.py
nodeId: reconcile-output-sync
parent: main/sidekick-checkin
related:
  - sidekick-sync/reconcile-output
  - session-startup/reconcile-output-sync
slug: reconcile-output-sync
status: current
summary: Both-way output/artifacts sync sweep via the bundled sidekick-sync MCP server (reconcile_output) against the external storage base path, resolving each reported conflict through the picker and resolve_output.
systems:
  - mcp-server
type: integration
---

## TLDR (agent)
**Purpose:** Two-way reconcile of each project's `output/` (and `artifacts/`) with the external storage base path, then route every reported conflict to the user.
**Inputs:** trigger: check-in sweep per project after approvals (only if Output sync on AND a base path set); calls `reconcile_output` with ABSOLUTE project path + `base`; manifest `.sidekick/sync.json` as baseline.
**Outputs:** native binary-safe file copies in/out (additive); result `pushed/pulled/conflicts/errors`; per conflict a picker question + `resolve_output`; then checkin-close.
**Code anchor:** [skills/sidekick-core/scripts/sync_server.py](../../../skills/sidekick-core/scripts/sync_server.py)
**Edges:** ← sidekick-checkin/per-project-walk (parent), → sidekick-checkin/checkin-close (starts)
**Key rules:**
- Runs only when Output sync is on AND an Output sync base path is set and reachable; otherwise skipped silently.
- Pass the ABSOLUTE project path (`<workspace root>/projects/<slug>`) — a relative path resolves wrong in the server and silently syncs nothing.
- Sync is additive: a one-sided delete is never propagated; never base64 a file through the model.
- A conflict is never resolved silently — ask via the picker (keep Cowork / keep external / keep both), then call `resolve_output`.
- A failed step / unreachable base path is reported, not fatal.

## Functional (user facing)

### Why use this?
When you've turned on output sync, this is the step that keeps your finished work and live dashboards in step with the shared storage folder — your Google Drive or OneDrive — in both directions. Deliverables you produced land where you and your colleagues keep files; edits someone made there flow back into the workspace; and nothing is decided on your behalf when the two sides genuinely disagree.

### When it runs
It runs as a per-project sweep near the end of the check-in, after the project's approvals have been carried out — and only when you've switched output sync on and set a storage folder for it. If sync is off, or no folder is set, this step simply doesn't happen.

### What it talks to
Your external storage folder — a mounted or synced Drive/OneDrive location you chose in settings. Under it, each project mirrors its `output/` (and the generated dashboard `artifacts/`) into a per-project subfolder. Only those two folders are synced; your brain, logs, and data stay private to the workspace.

### Behind the scenes
For every file, the sweep compares both sides against a remembered baseline. If only one side changed, that change is copied over the other. If a file exists on just one side, it's copied across — so syncing never deletes; to remove a deliverable you delete it on both sides. If both sides changed the same file, that's a conflict: it's left untouched and brought to you. A routine pull of an edit you made deliberately applies without asking — having sync on is your standing consent — and only a true conflict stops to ask.

### When both sides changed a file
You're asked, one file at a time, whether to keep the workspace version, keep the external version, or keep both. "Keep both" preserves your file and saves the other one alongside it with a "from-external" suffix, on both sides, so nothing is lost.

### Pro tips
- If something didn't sync, the step tells you what failed and carries on — it never blocks a local write or deletes data, and the next session-start or check-in retries.
- A deliverable that reappears after you deleted it usually means it still existed on the other side — delete on both to remove it for good.
- Edits you make directly in the Drive folder are first-class; they flow back in on the next sweep.

### Related
- [per-project-walk](per-project-walk.md) — the step that calls this sweep per project.
- [checkin-close](checkin-close.md) — the wrap-up that follows the sweep.

## Technical

External boundary: the local `output/`+`artifacts/` trees vs. a mounted storage drive (Google Drive for Desktop / OneDrive). All file movement crosses through the bundled **`sidekick-sync`** MCP server (`skills/sidekick-core/scripts/sync_server.py`, stdlib Python, declared in `.claude-plugin/plugin.json` under `mcpServers`) — never the model, a connector, or a sandboxed shell (ARCHITECTURE §7c gives the three test-driven reasons: no bytes through the model, the bash sandbox's writes don't trigger the storage client, a native host process does).

- **Tools called.** `reconcile_output(project, base)` → `sync.reconcile(...)`; `resolve_output(project, base, file, keep)` → `sync.resolve(...)` (`_call_tool` in `sync_server.py`). The project arg must be the **absolute** path; `_resolve_project` is intolerant of a relative path (it resolves wrong and the server silently syncs nothing). `keep ∈ local|external|both`; `both` keeps the local file and writes the external one as `<name>.from-external<ext>` on both sides.
- **Reconcile rule.** Baseline manifest `projects/<slug>/.sidekick/sync.json` (path → last-synced content hash, in hidden `.sidekick/` so it is never itself synced). Per file across local ∪ external ∪ manifest: same content → in sync; one side changed → copy over the other; both changed (or no baseline + differing contents) → conflict, left untouched + reported; one side only → copied (additive); gone both sides → dropped from manifest. Manifest rewritten after. First sync (no manifest) treats every file as new — no false conflicts.
- **Conflict handling.** Reconcile never resolves; the model asks via the picker (keep Cowork / external / both) and calls `resolve_output`. Result fields surfaced: `pushed`, `pulled`, `conflicts`, `errors`.
- **Gating + failure.** Runs only when **Output sync = yes** and an **Output sync base path** is set (ARCHITECTURE §8) and reachable; otherwise skipped silently. Unreachable base path or a failed copy → reported in `errors`, non-fatal; never blocks a local write or deletes data; next session-start/check-in reconcile retries. Deploy dependency: host must launch the MCP server (Python on PATH, or an absolute interpreter in the manifest `command`); if `sidekick-sync` tools are unavailable the model falls back to the `sync.py` CLI and warns a sandboxed copy may not reach the storage client. Full protocol: `skills/sidekick-core/references/sync-discipline.md`.

**Dependencies.** Parent `sidekick-checkin/per-project-walk` calls this sweep (and `sidekick-checkin/distill-log-to-brain` also calls it after approvals). Starts `sidekick-checkin/checkin-close`. Shares its engine with the `scripts/sync.py` CLI (same `sync` functions). No gatekeepers added here — the deliverable was already confirmed under the output gatekeeper (ARCHITECTURE §7).
