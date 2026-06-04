# Output sync — the protocol

Loaded on demand by the `sidekick` skill when **Output sync** is on. Defines
how a project's `output/` **and `artifacts/`** are kept in step, both ways, with
an external storage folder — efficiently, without routing file bytes through the
model. (`artifacts/` holds generated dashboard HTML; syncing it to Drive is what
lets a live dashboard wrapper read it — see `reporting.md`.)

## Why a native MCP server (not the connector, not a shell copy)

Two failures in testing shaped this:

- **Connector upload made the model base64 the file** into its own output
  (~size×1.33 tokens, token-by-token) — an Excel push that ran past five
  minutes.
- **A shell copy from the Bash sandbox didn't sync.** The sandbox writes to a
  Linux mountpoint; Google Drive for Desktop / OneDrive never get the
  filesystem notification, so nothing uploads — confirmed in testing (a CLI
  `reconcile` reported success but the file never appeared in Drive).

The fix: the plugin ships a small **MCP server** (`scripts/sync_server.py`,
stdlib-only) declared in `.claude-plugin/plugin.json` under `mcpServers`. A
plugin MCP server runs as a **native host process**, so its **file copies land
on the real filesystem the storage client watches** and sync triggers. The
model calls its tools with **paths only** — file bytes never pass through the
model.

The same engine is also a CLI (`scripts/sync.py`) for environments where the
shell is already native (and for local testing); both call the identical
functions in `sync.py`.

## The tools (provided by the `sidekick-sync` MCP server)

- **`reconcile_output(project, base)`** — two-way sync of `project`'s `output/`
  and `artifacts/` with `<base>/<slug>/{output,artifacts}/`. **`project` must be the ABSOLUTE path** to the
  project dir, e.g. `C:\Claude Cowork\Sidekick\projects\finance` — the server
  runs in its own process, so a relative path resolves against the wrong
  directory (in Cowork a scratchpad) and silently syncs nothing. `base` is the
  **Output sync base path** from settings. Returns JSON: `pushed`, `pulled`,
  `in_sync`, `conflicts`, `errors`, `warnings`. Never resolves a conflict
  itself.
- **`resolve_output(project, base, file, keep)`** — settle one conflict;
  `keep` ∈ `local | external | both` (`both` keeps the local file and the
  external one as `<name>.from-external<ext>` on both sides).

(The exact tool names surface at runtime, namespaced by the host, e.g.
`mcp__sidekick-sync__reconcile_output`. The CLI equivalents are
`sync.py reconcile` / `sync.py resolve`.)

## Layout

One **base path** in `sidekick.settings.md` (**Output sync base path**) — a
mounted/synced folder, e.g. `G:\My Drive\sidekick`. Under it, per project:

```
<base path>/                          e.g. G:\My Drive\sidekick
├── <project-a>/
│   ├── output/        ↔ projects/<project-a>/output/      (deliverables; area subfolders included)
│   └── artifacts/     ↔ projects/<project-a>/artifacts/   (dashboard HTML; read by the live wrapper)
└── <project-b>/ …
```

No `sidekick-` prefix — the base path the user chose is the Sidekick root.
Manifest keys are `<sub>/<relpath>` (e.g. `artifacts/seasonality.html`).

## How reconcile decides (per file)

A manifest `projects/<slug>/.sidekick/sync.json` (path → last-synced content
**hash**; in the hidden `.sidekick/` state folder, never inside
`output/`/`artifacts/`, so it isn't synced) holds the baseline:

| Situation | Action |
|---|---|
| Same content both sides | in sync |
| One side changed vs baseline | copy the changed side over the other |
| **Both** changed vs baseline (or no baseline, contents differ) | **conflict** — left untouched, reported |
| File on one side only | copied to the other (**additive**) |
| Gone on both sides | dropped from the manifest |

**Additive — sync never deletes.** A file present on only one side is copied
to the other, so a delete on one side is **not propagated**; to remove a
deliverable, delete it on **both** sides. (Favours never losing data; a
one-sided delete is re-created from the surviving side.)

## How the model uses it

1. **Only when Output sync is on AND a base path is set.** No base path → sync
   does not run.
0. **Always pass the ABSOLUTE project path.** Determine the workspace root (the
   absolute dir holding `sidekick.settings.md`; your file context knows it, or
   run `pwd` / `Get-Location`) once per session, and pass
   `<root>/projects/<slug>`. A `warnings` entry about a missing local dir means
   the path was wrong/relative — fix and retry.
2. **Push after a confirmed output write:** call `reconcile_output`.
3. **Pull + reconcile at session start (active project) and at the check-in:**
   call `reconcile_output`.
4. **On `conflicts`:** for each file, ask the user via the **picker** — keep
   the Cowork version, keep the external, or keep both — then call
   `resolve_output`. Never overwrite a conflict silently.
5. **On `errors` / unreachable base path:** report what didn't sync and
   continue. Sync never blocks a local write and never deletes data.
6. **Never** base64 a file, hand-read bytes, or push a binary through a
   connector — moving files is the tool's job.
7. **If the `sidekick-sync` tools are not available** (server didn't start —
   see below), fall back to the `sync.py` CLI and tell the user that sync may
   not reach the storage client until the server runs.

## Deployment notes / one-time test

- The server is launched by the host as `python <plugin>/…/sync_server.py`.
  **Python must be on the host PATH.** If the tools don't appear after
  install, set the `command` in `plugin.json` `mcpServers` to an absolute
  interpreter path (e.g. `C:\\Python312\\python.exe`).
- **Verify once:** with a base path set, create a small deliverable, run
  `reconcile_output`, and confirm the file shows up in the storage client
  (Drive/OneDrive web/app), not just on disk. If `pushed` lists it but it
  never appears in the client, the server isn't reaching the watched
  filesystem in this environment — report it.

## Performance note

`reconcile` hashes files on both sides. On a "files on demand" mount, hashing
an external file may pull it down first; the first reconcile of a large store
is slower. Later runs only copy what changed.
