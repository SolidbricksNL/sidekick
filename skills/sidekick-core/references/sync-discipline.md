# Output sync — the protocol

Loaded on demand by the `sidekick` skill when **Output sync** is on. Defines
how a project's `output/` is kept in step, both ways, with an external storage
folder — efficiently, without ever routing file bytes through the model.

## Why a CLI, not the connector

Pushing a file through a storage **connector** forced the model to
**base64-encode the bytes into its own output** — ~size×1.33 tokens emitted
token-by-token. A single Excel push ran past five minutes in testing. Writing
to the OS-mounted storage folder from the **bash sandbox** didn't work either:
the sandbox writes to a Linux mountpoint and the storage client (Google Drive
for Desktop, OneDrive) never gets the filesystem notification, so nothing
syncs.

The fix: a small **CLI** (`scripts/sync.py`, stdlib only) that does plain
**file copies** between the local `output/` and a configured **base path** on
the mounted storage. Copies are binary-safe and cost **zero model tokens**.
Run where it writes to the real filesystem the storage client watches, the copy
triggers a normal sync.

> **Execution requirement (verify in your environment).** The copy only
> triggers the storage client if it lands on the filesystem that client
> watches (the native Windows path, e.g. `G:\My Drive\…`). If the CLI runs in
> a sandbox that writes to a Linux mountpoint instead, the client may not
> notice. Test once (below). If a shell-invoked CLI can't reach the watched
> filesystem, the same engine can be wrapped as a small native MCP server —
> the sync logic does not change.

## Layout

One **base path** is configured in `sidekick.settings.md` (**Output sync base
path**) — a mounted/synced folder, e.g. `G:\My Drive\sidekick`. Under it,
per project:

```
<base path>/
├── <project-a>/
│   └── output/        ↔ projects/<project-a>/output/   (mirrors the tree, area subfolders included)
└── <project-b>/
    └── output/        ↔ projects/<project-b>/output/
```

The project folder name is the project slug; `output/` sits inside it. No
`sidekick-` prefix — the base path itself is the Sidekick root the user picked.

## The CLI

```
python3 "$CLAUDE_PLUGIN_ROOT/skills/sidekick-core/scripts/sync.py" \
    reconcile --project projects/<slug> --base "<base path>" [--dry-run]
```

`reconcile` does the safe two-way sync and prints a JSON summary:
`pushed`, `pulled`, `in_sync`, `conflicts`, `errors`. It **never** resolves a
conflict on its own. `--dry-run` reports planned actions and changes nothing.

```
python3 "$CLAUDE_PLUGIN_ROOT/skills/sidekick-core/scripts/sync.py" \
    resolve --project projects/<slug> --base "<base path>" --file <relpath> --keep local|external|both
```

`resolve` settles one conflict the user decided on. `both` keeps the local
file under its name and the external one as `<name>.from-external<ext>`, on
both sides.

### How reconcile decides (per file)

A manifest `projects/<slug>/.sidekick-sync.json` (path → last-synced content
hash; at the **project root**, never inside `output/`, so it isn't synced)
holds the baseline:

| Situation | Action |
|---|---|
| Same content both sides | in sync |
| One side changed vs baseline | copy the changed side over the other |
| **Both** changed vs baseline (or no baseline, contents differ) | **conflict** — left untouched, reported |
| File on one side only | copied to the other (**additive**) |
| Gone on both sides | dropped from the manifest |

**Additive — sync never deletes.** A file present on only one side is copied
to the other, so a delete on one side is **not propagated**; to remove a
deliverable, delete it on **both** sides. (This favours never losing data;
it does mean a one-sided delete is re-created from the surviving side.)

## How the model uses it

1. **Only when Output sync is on AND a base path is set.** No base path → sync
   does not run (there is no connector fallback for files).
2. **Push after a confirmed output write.** After creating/editing a
   deliverable, run `reconcile` so it copies out. No extra confirmation — the
   setting is the consent.
3. **Pull + reconcile at session start (active project) and at the check-in.**
   Run `reconcile` to bring external edits in and push local ones out.
4. **On `conflicts`:** for each conflicting file, ask the user via the
   **interactive picker** — keep the Cowork version, keep the external
   version, or keep both — then call `resolve --keep …`. Never overwrite a
   conflict silently.
5. **On `errors` / unreachable base path:** report what didn't sync and
   continue. Sync never blocks a local write and never deletes data.
6. **Never** base64 a file, hand-read bytes, or push a binary through a
   connector. Moving files is the CLI's job, via copies.

## One-time test (do this before trusting sync)

1. Set a base path to your mounted storage folder.
2. Create a small deliverable, run `reconcile`, and check it appears in the
   storage client (web/app), not just on disk.
3. If it does **not** appear, the CLI isn't reaching the watched filesystem in
   your environment — note it; the MCP-server wrapper is the fallback.

## Performance note

`reconcile` hashes files on both sides. On a "files on demand" mount, hashing
an external file may pull it down first; expect the first reconcile of a large
store to be slower. Subsequent runs only copy what changed.
