---
kind: curated
status: current
---

# Sidekick — brain index

Sidekick is a role-adaptive personal-advisor plugin for **Claude Cowork**.
It fixes Cowork's two sprawl failure modes — everything-in-chat and
scattered documents — by anchoring all work in flat **projects** and
enforcing three strictly separated **write disciplines**: a free `log/`,
a diff-and-approval `brain/`, and a confirm-before-write `output/` +
structured `data/`. It ships as nine Markdown skills plus a native
`sidekick-sync` MCP server, all derived from the canonical
`docs/ARCHITECTURE.md`.

Start at the `## TLDR (agent)` block of any node. Use `flow/_index.json`
for deterministic lookups, or open `flow-viewer.html` to browse visually.

## Top-level subflows

**The skills (user-facing surfaces)**

- **Sidekick Core** — always-on backbone: project detection, the three
  write disciplines, the surface gate → @.solidcortex/flow/sidekick-core/_flow.md
  - sub-areas: surface-gate, session-startup, project-detection,
    write-disciplines, structured-data
- **Sidekick Init** — `/sidekick-init` setup wizard → @.solidcortex/flow/sidekick-init/_flow.md
- **Sidekick Guide** — `/sidekick-guide` onboarding tour → @.solidcortex/flow/sidekick-guide/_flow.md
- **Sidekick Report** — `/sidekick-report` recipes + dashboards → @.solidcortex/flow/sidekick-report/_flow.md
- **Sidekick Check-in** — `/sidekick-checkin` action loop → @.solidcortex/flow/sidekick-checkin/_flow.md
- **Sidekick Triage** — `/sidekick-triage` scheduled inbound scan → @.solidcortex/flow/sidekick-triage/_flow.md
- **Sidekick Status** — `/sidekick-status` read-only overview → @.solidcortex/flow/sidekick-status/_flow.md
- **Sidekick Find** — `/sidekick-find` cross-project recall → @.solidcortex/flow/sidekick-find/_flow.md
- **Sidekick Archive** — `/sidekick-archive` retire a project → @.solidcortex/flow/sidekick-archive/_flow.md

**External & dev surfaces**

- **Sidekick Sync MCP Server** — native two-way output/artifact sync,
  dashboard builds, report registry → @.solidcortex/flow/sidekick-sync/_flow.md
- **Packaging & Validation** — manifest, self-marketplace, structure
  validator, CI, pre-commit hook → @.solidcortex/flow/packaging/_flow.md

## Where to look

- The design source of truth is `docs/ARCHITECTURE.md` (every skill is
  derived from it).
- The install-truncation cap (~15808 bytes) on every `skills/` runtime
  file is the project's load-bearing constraint — see the **packaging**
  subflow.
