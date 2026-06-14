---
flowId: sidekick-sync
nodeId: resolve-output
slug: resolve-output
status: current
kind: derived
summary: The resolve_output tool — settles one output-sync conflict the user chose (keep local, external, or both), copying the surviving file across the host/Drive boundary and updating the manifest.
systems: [mcp-server]
domains: [output-sync]
parent: sidekick-sync/mcp-server
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## Technical

**Entry point.** The `resolve_output` MCP tool is declared in `skills/sidekick-core/scripts/sync_server.py` (`_TOOLS[1]`) and dispatched by `_call_tool` as `sync.resolve(proj, args["base"], args["file"], args["keep"])`, wrapped in `_ok`. Input schema requires `project`, `base`, `file` (a conflicting relative path under `output/`), and `keep` with `enum: ["local","external","both"]`. A missing argument surfaces as a `KeyError` → MCP "missing argument" error; a missing-file `RuntimeError` surfaces as a tool error.

**Engine call.** Body in `skills/sidekick-core/scripts/sync.py::resolve(project, base_path, file, keep)`. `_paths` yields `(proj, base_root=<base>/<name>, mpath, name)`; `files = _load_manifest(mpath)`. `k = file` is a manifest key `"<sub>/<relpath>"`; `lp = proj/k`, `rp = base_root/k`.

**Per-choice behaviour.**
- `keep == "local"`: raises `RuntimeError` if `lp` is missing; else `_copy(lp, rp)` and `files[k] = _hash(lp)`.
- `keep == "external"`: raises if `rp` is missing; else `_copy(rp, lp)` and `files[k] = _hash(rp)`.
- `keep == "both"`: raises if `rp` is missing. Computes `alt = <stem>.from-external<suffix>` (posix). Copies external → `proj/alt`, then `proj/alt` → `base_root/alt`, recording `files[alt]`. If `lp` exists, the local file keeps the original name on both sides (`_copy(lp, rp)`, `files[k] = _hash(lp)`). So `both` yields the local file under `k` and the external file under `alt`, on both sides.

After the branch, `_save_manifest` rewrites the manifest so the resolved file is now a settled baseline (a subsequent reconcile sees it in sync, not as a fresh conflict). Returns `{ok:true, action:"resolve", project:name, file:k, keep}`.

**CLI parity.** `cmd_resolve` exposes the same call as `sync.py resolve --project --base --file --keep`; `_die` prints `error: <msg>` on `RuntimeError`. The CLI is for native-shell/local-testing environments; the production path is the MCP tool.

**Boundary rationale.** `integration` because the surviving copy must reach the host filesystem the storage client watches — same host/Drive boundary as sidekick-sync/reconcile-output. This node is reached only after reconcile reports a conflict and the user answers the picker (ARCHITECTURE §7c, "Conflicts go to the human"). Copies use the same binary-safe `_copy`/`_hash` primitives as the engine (see sidekick-sync/sync-engine).
