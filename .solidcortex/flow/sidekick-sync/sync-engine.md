---
flowId: sidekick-sync
nodeId: sync-engine
type: process
slug: sync-engine
status: current
kind: derived
summary: The shared sync engine in sync.py — binary-safe file copies plus the per-file manifest reconcile rule (push/pull/in-sync/conflict via a sha256 baseline) that backs both reconcile_output and resolve_output.
systems: [python-helpers]
domains: [output-sync]
parent: main/sidekick-sync
mainCodeFile: skills/sidekick-core/scripts/sync.py
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** The shared sync engine — binary-safe copies plus the per-file manifest reconcile rule that backs both reconcile_output and resolve_output.
**Inputs:** A project dir and an external base path; the two synced subdirs `output/` and `artifacts/`; the `.sidekick/sync.json` manifest as sha256 baseline.
**Outputs:** Files copied between local and external; a rewritten manifest; a summary dict per operation. Also a standalone CLI (`sync.py reconcile|resolve`).
**Code anchor:** [skills/sidekick-core/scripts/sync.py](../../../skills/sidekick-core/scripts/sync.py)
**Edges:** (none)
**Key rules:**
- Per-file decision uses three states — local hash, external hash, baseline hash — to classify push / pull / in-sync / conflict.
- Dotfiles and dot-folders are skipped on both sides, so the `.sidekick/` manifest never syncs itself.
- Copies are `shutil.copy2` (binary-safe, metadata-preserving); a one-sided-only file is copied across (additive, never deleted).

## Functional (user facing)

### Why use this?
This is the quiet machinery under output syncing. You never call it by name, but it is what actually decides, file by file, which side is newer and copies it the right way — and it is shared by both the everyday two-way sync and the conflict-resolution step, so they always agree on what "in sync" means.

### What it does
- Keeps a project's `output/` and `artifacts/` folders in step with the matching folders under your external base path.
- Decides each file's fate by comparing the local copy, the external copy, and a remembered baseline — copying the side that changed and flagging the case where both changed.
- Copies files byte-for-byte, so spreadsheets, images, and HTML survive intact.
- Remembers what it last synced in a small baseline file kept out of the synced folders, so it never tries to sync its own bookkeeping.
- Also works from a real terminal as a command-line tool, which is handy for local testing.

### Behind the scenes
Each file is identified by its folder and path and fingerprinted with a content hash. The first time through there is no baseline, so everything simply copies across — no false alarms. After every run the baseline is rewritten to reflect the new reality. A file that only one side has is treated as new and copied over (so nothing is lost), which is also why deleting a file on just one side does not make it disappear — the surviving copy comes back next time.

### Pro tips
- This engine is the single source of truth for the sync rule; the native MCP tools just call into it, which is why the host run and a command-line run behave identically.
- If a sync reports that files could not be read, the external storage path is probably unreachable — that is the engine refusing to guess rather than corrupting the baseline.

### Related
- sidekick-sync/reconcile-output — the host-side tool that runs this engine's two-way pass.
- sidekick-sync/resolve-output — the host-side tool that runs this engine's conflict settlement.

## Technical

**Main code.** `skills/sidekick-core/scripts/sync.py` (~234 LOC) — dependency-free stdlib (argparse, hashlib, json, shutil, pathlib). Exposes `reconcile` and `resolve` (called by the native MCP server) plus a CLI (`reconcile`/`resolve` subcommands) for native-shell and local-testing use. Kept small because Cowork truncates large plugin files on install.

**Constants.** `_CHUNK = 65536` (hash read size); `_SUBDIRS = ("output", "artifacts")` — the only two project subfolders synced.

**Path + manifest helpers.** `_paths(project, base)` → `(proj, base_root=<base>/<name>, mpath=proj/.sidekick/sync.json, name)`, migrating a legacy root-level `.sidekick-sync.json` into `.sidekick/` on first access. `_walk(root)` maps relative-posix-path → absolute Path for every regular file, skipping any name or ancestor part starting with `.` (so the `.sidekick/` state folder never syncs). `_hash` is chunked sha256; `_copy` is `shutil.copy2` with parent mkdir (binary-safe, metadata-preserving). `_load_manifest`/`_save_manifest` read/write `{version:1, files:{key:sha256}}` (`files` only); a write failure warns to stderr rather than aborting.

**`reconcile(project, base_path, dry_run=False)`.** Builds `Lmap`/`Rmap` keyed `"<sub>/<relpath>"` across both subdirs, hashes both sides (`lh`/`rh`; an OSError → `RuntimeError("could not read files (storage path reachable?)")`, the unreachable-mount signal). Iterates `sorted(set(lh) | set(rh) | set(base))` and applies the three-state rule (`b`=baseline, `l`=local, `r`=remote): equal → in-sync; `l==b` → pull; `r==b` → push; neither==b (or no baseline) → conflict (reported, untouched); one-side-only → additive copy; baseline-only → dropped. `_copy` performs the move unless `dry_run`. Rewrites `new` into the manifest; per-file OSErrors collect into `errors`. Returns `{ok, action:"reconcile", project, base, subdirs, dry_run, pushed[], pulled[], in_sync, conflicts[], errors[], warnings[]}` (warnings flag a relative project path or a missing local subdir).

**`resolve(project, base_path, file, keep)`.** Settles one manifest key. `keep ∈ {local, external, both}`: `local`/`external` copy the chosen side over the other and rehash; `both` keeps local under the original name and external under `<stem>.from-external<suffix>` on both sides. Missing chosen-side file → `RuntimeError`. Rewrites the manifest so the resolved file becomes an in-sync baseline. Returns `{ok, action:"resolve", project, file, keep}`.

**CLI.** `build_parser` wires `reconcile` (`--project`, `--base`, `--dry-run`) and `resolve` (`--project`, `--base`, `--file`, `--keep`) to `cmd_reconcile`/`cmd_resolve`, which `_emit` the JSON and `_die("error: …")` on `RuntimeError`.

**Dependencies / consumers.** No internal node deps. Consumed by `sync_server.py` (the `sidekick-sync` MCP server) for `reconcile_output` (sidekick-sync/reconcile-output) and `resolve_output` (sidekick-sync/resolve-output). The host/Drive-boundary rationale (native copies reach the watched filesystem; sandbox-shell copies do not; no bytes through the model) is in `docs/ARCHITECTURE.md` §7c.
