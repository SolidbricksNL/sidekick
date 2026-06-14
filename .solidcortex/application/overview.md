---
kind: derived
status: current
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

# Sidekick

## Stack
- Claude Cowork plugin — packaged as Markdown skills, not a compiled app
- Language: Markdown (skills, commands, docs) + Python 3 (stdlib only) + a small Node.js (ESM) validator
- Plugin manifest: `.claude-plugin/plugin.json` (declares the `sidekick-sync` MCP server) + `.claude-plugin/marketplace.json` (self-marketplace catalog)
- Native MCP server: `sidekick-sync` (`scripts/sync_server.py`, launched via `python`) for two-way file sync and dashboard builds
- Structured-data helper: stdlib Python `data.py` (throwaway in-memory SQLite over plain JSON tables)
- Presentation: dependency-free UI kit (`ui.css` / `ui.js` / `solidbricks.png`) baked into self-contained dashboard HTML by `dashboard.py`
- Quality gate: `scripts/validate-structure.mjs` Node validator + GitHub Actions CI (`.github/workflows`) + a `scripts/hooks/pre-commit` hook
- No traditional package manager / build step — install = Cowork loading the skill files

## Entry points
- `.claude-plugin/plugin.json` — plugin manifest, registers the `sidekick-sync` MCP server
- `.claude-plugin/marketplace.json` — marketplace catalog Cowork installs the plugin from
- `skills/sidekick-core/SKILL.md` — the always-on, model-invoked backbone skill
- `skills/sidekick-core/scripts/sync_server.py` — `sidekick-sync` MCP server process entry
- `commands/*.md` — flat wrappers that register the typed `/sidekick-*` commands
- `scripts/validate-structure.mjs` — structural validator run by CI and the pre-commit hook

## High-level architecture
Sidekick is a role-adaptive personal-advisor plugin for Claude Cowork that fixes Cowork's two sprawl
failure modes (everything-in-chat, scattered documents) by anchoring all work in flat **projects** and
enforcing three strictly separated **write disciplines**: a free `log/`, a diff-and-approval `brain/`,
and a confirm-before-write `output/` + structured `data/`. Behavior is split across nine Markdown
skills — the always-on `sidekick-core` plus typed skills for init, triage, check-in, archive, status,
find, report, and guide — each derived from the canonical `docs/ARCHITECTURE.md`. Structured data lives
as plain JSON tables reached only through `data.py`; the reporting layer turns those tables into saved
recipes and self-contained dashboards built from a shared UI kit. A native `sidekick-sync` MCP server
keeps each project's `output/` and `artifacts/` in two-way step with an external storage folder, because
sandboxed shell copies do not reach the storage client. Because the plugin installs user-level and loads
on every Claude surface, a **surface gate** keeps it inert outside a real Cowork workspace. A Node
validator plus CI and a pre-commit hook guard the ~15808-byte Cowork install-truncation cap on every
runtime file.
