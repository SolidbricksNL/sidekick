---
flowId: sidekick-sync
nodeId: reconcile-output
slug: reconcile-output
status: current
kind: derived
summary: The reconcile_output tool — two-way reconciles a project's output/ and artifacts/ against the external storage base path, crossing the host/Drive boundary the sandboxed shell cannot reach.
systems: [mcp-server]
domains: [output-sync]
parent: sidekick-sync/mcp-server
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## Technical

**Entry point.** The `reconcile_output` MCP tool is declared in `skills/sidekick-core/scripts/sync_server.py` (`_TOOLS[0]`) and dispatched by `_call_tool`: it calls `_resolve_project(args["project"])` then `sync.reconcile(proj, args["base"])`, wrapping the returned dict in `_ok`. Input schema requires `project` (described as ABSOLUTE) and `base`; the tool description forbids self-resolving conflicts.

**Engine call.** The body lives in `skills/sidekick-core/scripts/sync.py::reconcile(project, base_path, dry_run=False)` (the shared engine documented under sidekick-sync/sync-engine). The MCP path never passes `dry_run`, so the server form always writes; the `--dry-run` flag exists only on the CLI (`cmd_reconcile`).

**Paths and manifest.** `_paths` derives `(proj, base_root=<base>/<name>, mpath=proj/.sidekick/sync.json, name)`. A legacy root-level `.sidekick-sync.json` is migrated into `.sidekick/sync.json` on first access. The manifest is the per-file baseline (`{version, files: {key: sha256}}`); keys are `"<sub>/<relpath>"` over the two synced subdirs `("output", "artifacts")`.

**Reconcile algorithm.** `_walk` builds local (`Lmap`) and external (`Rmap`) maps of `"<sub>/<rel>" → Path`, skipping any dotfile/dotdir. Hashes `lh`/`rh` are computed with `_hash` (chunked sha256); a read failure raises `RuntimeError("could not read files (storage path reachable?)")` — the signal that the Drive mount is unreachable. For each key in `set(lh) | set(rh) | set(base)`:
- both present, equal → in sync, baseline kept;
- both present, `l == baseline` → pull (copy external over local);
- both present, `r == baseline` → push (copy local over external);
- both present, neither equals baseline (or no baseline) → conflict, reported, baseline kept if known;
- local only → push (additive); external only → pull (additive);
- present only in baseline → dropped from manifest.

Copies go through `_copy` (`shutil.copy2`, mkdir parents) — binary-safe. After the pass, `_save_manifest` rewrites `new`. OSErrors per file are collected into `errors` rather than aborting.

**Return shape.** `{ok, action:"reconcile", project, base, subdirs, dry_run, pushed[], pulled[], in_sync:int, conflicts[], errors[], warnings[]}`. `warnings` flags a relative project path and a missing local `output/artifacts` dir.

**Boundary rationale.** This is an `integration` node because the copy must land on the host filesystem the storage client watches; a write from the bash sandbox to the mount reported success but never reached Drive (ARCHITECTURE §7c). Running the copy inside the native MCP host process is what makes the storage client's sync actually fire. Conflicts are deferred to sidekick-sync/resolve-output.
