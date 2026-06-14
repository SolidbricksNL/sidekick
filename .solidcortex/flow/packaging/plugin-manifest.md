---
flowId: packaging
nodeId: plugin-manifest
type: process
slug: plugin-manifest
status: current
kind: derived
summary: Plugin manifest declaring the plugin name, release metadata, and the sidekick-sync MCP server registration; a string repository field is what makes Cowork accept the typed commands.
systems: [plugin-manifest, mcp-server]
domains: [dev-tooling]
parent: main/packaging
mainCodeFile: .claude-plugin/plugin.json
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Plugin manifest that declares the plugin name and release metadata and registers the `sidekick-sync` MCP server.
**Inputs:** Loaded by Cowork on install; read at marketplace-resolve time and at MCP startup.
**Outputs:** A valid plugin definition + one running `sidekick-sync` MCP server (`python sync_server.py`).
**Code anchor:** [.claude-plugin/plugin.json](../../../.claude-plugin/plugin.json)
**Edges:** ← packaging/marketplace-catalog (installed via this manifest)
**Key rules:**
- `name` is required and non-empty; the always-on skill is `sidekick-core`, kept distinct from the plugin name `sidekick`.
- `repository` MUST be a STRING — an object value fails manifest validation and made Cowork load skills but reject every typed command.
- The MCP server path uses `${CLAUDE_PLUGIN_ROOT}` (not a shell var) so it resolves wherever the plugin is installed.

## Functional (user facing)

### Why use this?
This is the identity card Cowork reads to install Sidekick: it names the plugin, carries its version and description, and switches on the one background service Sidekick needs — the sync server that copies deliverables to and from your connected storage.

### What it does
- Names the plugin `sidekick` and stamps the current release version and description.
- Records author, license, homepage, repository, and search keywords.
- Registers a single MCP server, `sidekick-sync`, launched as a Python process when the plugin loads.

### Behind the scenes
The manifest is the historical install-blocker: for several early iterations every typed command failed because the `repository` field was an object, which is invalid against Cowork's manifest schema. Cowork still discovered the skills on the filesystem, but a malformed manifest meant it refused to register the commands — surfacing as a confusing "Unknown command" error. Making `repository` a plain string fixed installation and command registration in one change.

### Pro tips
- The plugin is deliberately named `sidekick` while the always-on skill is `sidekick-core`; a skill folder literally named `sidekick` would collide with the plugin and break command resolution.
- The sync server is wired here, but it only does useful work once a project has an output/storage path configured.

### Related
- packaging/marketplace-catalog — the catalog that points at this manifest.
- packaging/structure-validator — enforces the string-`repository` rule.

## Technical
- **Main file:** `.claude-plugin/plugin.json` — Cowork plugin manifest; the second of the two files allowed in `.claude-plugin/`.
- **Required vs. optional:** only `name` is strictly required. `version`, `description`, `author` are present and warned-on-absence by the validator; `repository`, `license`, `keywords`, `homepage` are release-polish fields (warn-only).
- **`repository` type trap:** the schema wants a string. `scripts/validate-structure.mjs` Check 2 FAILs if `repository` is present but non-string — this guards the regression that broke command registration (object `{type,url}` → `repository: expected string, received object`).
- **MCP registration:** `mcpServers.sidekick-sync` runs `python ${CLAUDE_PLUGIN_ROOT}/skills/sidekick-core/scripts/sync_server.py`. `${CLAUDE_PLUGIN_ROOT}` is a Cowork-substituted placeholder (NOT a shell environment variable — it is not set in the shell), so the path resolves regardless of install location.
- **Dependencies:** resolved by `packaging/marketplace-catalog`; validated by `packaging/structure-validator` (Check 2). The registered server backs the two-way `output/`+`artifacts/` sync and the native dashboard build tools described in the docs/ layer.

