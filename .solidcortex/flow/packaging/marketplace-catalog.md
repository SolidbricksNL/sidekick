---
flowId: packaging
nodeId: marketplace-catalog
type: process
slug: marketplace-catalog
status: current
kind: derived
summary: Self-marketplace catalog listing the single sidekick plugin with source "./" so Cowork can add the repo as a marketplace and install the plugin from it.
systems: [plugin-manifest]
domains: [dev-tooling]
parent: main/packaging
mainCodeFile: .claude-plugin/marketplace.json
entry: true
edges:
  - to: packaging/plugin-manifest
    via: starts
    label: installs plugin via manifest
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Self-marketplace catalog that lists the single `sidekick` plugin so Cowork can add this repo as a marketplace and install the plugin from it.
**Inputs:** Cowork "add marketplace" pointed at the repo; reads `.claude-plugin/marketplace.json`.
**Outputs:** One installable plugin entry `sidekick` with `source: "./"` resolving to the repo root.
**Code anchor:** [.claude-plugin/marketplace.json](../../../.claude-plugin/marketplace.json)
**Edges:** → packaging/plugin-manifest (installs plugin via manifest)
**Key rules:**
- Exactly one plugin entry; `source` is `"./"` (plugin root = repo root) and must start with `./`.
- The self-listed plugin `name` must match `plugin.json` name (`sidekick`); a relative `source` must resolve to a `.claude-plugin/plugin.json`.
- Required top-level fields: `name`, `owner.name`, non-empty `plugins[]`.

## Functional (user facing)

### Why use this?
Cowork does not install a bare repository — it installs *plugins* that live inside *marketplaces*. This catalog is what turns the Sidekick repo into something Cowork recognizes: you add the repo as a marketplace once, and the single Sidekick plugin then appears as installable.

### What it does
- Declares one marketplace named `sidekick`, owned by Solidbricks.
- Lists exactly one plugin, also named `sidekick`, whose source is the repo root itself.
- Carries the short marketplace description shown when browsing.

### Behind the scenes
Because the plugin lives at the repo root (not in a subfolder), the catalog points its source at `"./"`. When Cowork resolves that source it expects to find the real plugin manifest at `.claude-plugin/plugin.json` alongside this catalog — that handoff is what actually installs Sidekick.

### Pro tips
- Adding the repo as a marketplace and installing the plugin are two separate steps in Cowork; this file only powers the first.
- If the plugin ever moves into a subfolder, the source string changes from `"./"` to that path — the catalog, not the manifest, owns that location.

### Related
- packaging/plugin-manifest — the manifest this catalog hands off to.

## Technical
- **Main file:** `.claude-plugin/marketplace.json` — Cowork marketplace catalog; one of only two files allowed in `.claude-plugin/` (the validator FAILs on any extra entry there).
- **Shape:** top-level `name`, `owner.name`, `metadata.description`, and `plugins[]`. Each plugin entry carries `name`, `source`, `description`.
- **Source resolution:** `source: "./"` means the plugin root is the repo root. `scripts/validate-structure.mjs` Check 2b asserts the source starts with `./` and that `<source>/.claude-plugin/plugin.json` exists, and warns if the self-referenced plugin name diverges from `plugin.json`'s `name`.
- **Dependencies:** consumed at install time by Cowork; validated by `packaging/structure-validator` (Check 2b). Hands off to `packaging/plugin-manifest`, which declares the actual plugin and its `sidekick-sync` MCP server.

