---
flowId: sidekick-find
nodeId: recall-query-intake
type: process
slug: recall-query-intake
status: current
kind: derived
summary: Receive the /sidekick-find query (or a recall question routed by sidekick-core), read chat language from settings, ask one clarifier if vague, and list non-archived projects to search.
systems: [skills, commands]
domains: [project-model, onboarding]
mainCodeFile: skills/sidekick-find/SKILL.md
entry: true
edges:
  - to: sidekick-find/search-markdown
    via: starts
    label: search brain/log/agenda
  - to: sidekick-find/probe-data-tables
    via: starts
    label: probe structured data
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Entry point of cross-project recall — captures the query, sets the chat language, narrows scope to searchable projects.
**Inputs:** `/sidekick-find <query>` command, or a recall question routed in by always-on sidekick-core; `sidekick.settings.md` (chat language).
**Outputs:** A validated query plus a list of non-archived `projects/` to fan out across; dispatches to search-markdown and probe-data-tables.
**Code anchor:** [skills/sidekick-find/SKILL.md](../../../skills/sidekick-find/SKILL.md)
**Edges:** → sidekick-find/search-markdown (starts), → sidekick-find/probe-data-tables (starts)
**Key rules:**
- Gate first: no `sidekick.settings.md` and no cowork MCP tools → say it isn't a Sidekick workspace and stop.
- Search only direct children of `projects/`, excluding archived ones.
- Ask at most one clarifying question, and only when the query is vague.

## Functional (user facing)

### Why use this?
This is the moment you ask Sidekick a question that no single project can answer on its own — "where did we decide the BPD pricing?", "which project has the Rabobank mandate?", "what do we know about Norvato?". The intake step takes that question, makes sure it understands what you mean, and lines up everywhere worth looking before the actual hunt begins.

### What it does
- Accepts your question two ways: you type `/sidekick-find` with the query, or you simply ask a recall question in passing and Sidekick recognises it as a cross-project lookup.
- Reads your workspace settings so the conversation continues in the language you set.
- Builds the shortlist of places to search: every active project, leaving archived ones out.
- Treats areas inside a project (its sub-folders) as part of that project, not as separate ones to list.

### When the query is vague
If the question is too broad to act on, Sidekick asks you exactly one short clarifying question before searching. You can answer in plain words — recall terms are open-ended, so there's no fixed format. Once you've narrowed it, the search runs.

### When this isn't a Sidekick workspace
If there's no Sidekick workspace marker and none of the Cowork tools are present (for example, you're in a plain chat or a code repository), Sidekick tells you this isn't a Sidekick workspace and stops rather than guessing.

### Behind the scenes
Once the query and project list are ready, two searches start in parallel: a text sweep of each project's notes and a probe of each project's structured data. Both feed their findings into the ranked results you eventually see.

### Pro tips
- You don't need the slash command — a clearly cross-project question is enough to trigger the recall.
- Archiving a finished project keeps it out of recall noise; it won't appear in results until you bring it back.

### Related
- sidekick-find/search-markdown — the text sweep this step launches.
- sidekick-find/probe-data-tables — the structured-data probe this step launches.
- sidekick-find/report-hits — where the combined results are ranked and shown.

## Technical

**Main code.** `skills/sidekick-find/SKILL.md` — the entire `sidekick-find` skill is one prose-instruction file (~63 lines); this node corresponds to its gate, "When you run", and step 1 of "How to search". The command alias `commands/sidekick-find.md` simply invokes the skill with the user's query.

**Intake sequence.**
1. Gate check (SKILL.md blockquote): absence of `sidekick.settings.md` AND absence of cowork MCP tools → refuse and stop. This mirrors the surface-gate pattern documented in `docs/ARCHITECTURE.md` (the plugin stands down outside Cowork).
2. Read `sidekick.settings.md` for the chat language used to frame replies.
3. Enumerate `projects/`, direct children only, skipping archived entries. A project's `brain/<area>/` or `output/<area>/` subfolders are subprojects/areas — searched under the parent, never listed as standalone projects.
4. If the query is vague, emit a single free-text clarifying question, then proceed.

**Routing.** This is the flow `entry: true` node. It fans out to two sibling process nodes that run against the same project list: `sidekick-find/search-markdown` (grep-style text recall) and `sidekick-find/probe-data-tables` (`data.py info`/`query`). Both ultimately converge on `sidekick-find/report-hits`.

**Invocation paths.** Either the explicit `/sidekick-find` command, or model-invocation: the always-on `sidekick-core` skill routes a clear recall question here without the command (see `docs/ARCHITECTURE.md` §11b). The whole skill is read-only — no node in this flow writes, distills, edits, or deletes.

**Dependencies.** `sidekick.settings.md` (presence = active workspace + chat language); the `projects/` directory layout (`project-structure.md` canonical layout). No Python, no MCP calls in this node itself.
