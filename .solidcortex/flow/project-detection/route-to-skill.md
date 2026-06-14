---
flowId: project-detection
nodeId: route-to-skill
type: process
slug: route-to-skill
status: current
kind: derived
summary: Once the active project is known, route a clear specialized intent (triage, check-in, status, find, report, archive) to the matching typed skill instead of handling it inline.
systems: [skills]
domains: [project-model]
parent: sidekick-core/project-detection
mainCodeFile: skills/sidekick-core/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Once a project is settled, hands a clearly specialized request to the matching typed Sidekick skill instead of improvising the work inline.
**Inputs:** trigger = a recognized specialized intent (triage, check-in, status, find, report, archive) within the active project; the related-skills register in the SKILL.
**Outputs:** control handed to the matching typed skill (`/sidekick-triage`, `/sidekick-checkin`, `/sidekick-status`, `/sidekick-find`, `/sidekick-report`, `/sidekick-archive`); core handles only general/inline work itself.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** ← project-detection/detect-active-project (clear specialized intent)
**Key rules:**
- Any "see / dashboard / chart / breakdown / show me" request goes to `sidekick-report` — never hand-build a view (hard rule).
- Spanning-recall questions ("where did we decide X?") route to `sidekick-find` rather than ad-hoc searching.
- Routing happens after the active project is known, not before.
- Core does the general work; the typed skills own their specialized flows.

## Functional (user facing)

### Why use this?
You get the right specialist for each kind of request automatically. When you ask to see your data, scan your inbox, walk through your projects, look something up across them, or archive a project, Sidekick hands the job to the tool built for it — so the result is consistent and complete instead of improvised on the spot.

### What it does
- Runs after Sidekick has settled which project you are in, as the last branch of project detection.
- Recognizes a handful of specialized intents and sends each to its dedicated skill rather than handling it inline.
- A request to see, chart, graph, or break down your stored data goes to the reporting skill — always, never a one-off hand-built chart.
- A "where did we decide X?" or other cross-project recall question goes to the find skill instead of an ad-hoc search.
- Inbox scans, project walk-throughs, cross-project overviews, and archiving each go to their own skill.
- Anything that is not one of these specialized jobs stays with the core advisor and is handled in the conversation.

### Behind the scenes
The specialized skills are the named entry points you can also invoke directly. Routing is a recognition step: core matches your intent to one of these flows and defers to it so the specialized rules (for example, how a dashboard is built, or how a check-in distils logs into the brain) are applied correctly. The reporting hand-off in particular is a hard rule — visualizing data is never freelanced inline.

### Pro tips
- You can always invoke a specialized skill yourself by name (for example asking for a status overview or a check-in) — routing just does it for you when your intent is clear.
- If a request spans multiple projects ("where did we land on the pricing question?"), let it route to find rather than asking Sidekick to search one project at a time.

### Related
- [detect-active-project](detect-active-project.md) — the step whose clear-specialized-intent branch arrives here.
- The typed skills it routes to: `/sidekick-triage`, `/sidekick-checkin`, `/sidekick-status`, `/sidekick-find`, `/sidekick-report`, `/sidekick-archive`.

## Technical

**Main code locations**
- `skills/sidekick-core/SKILL.md` — "Related skills" register names the six typed skills and what each owns; the "Showing data → ALWAYS the `sidekick-report` skill (hard rule)" section is the strongest routing rule (route every see/dashboard/chart/breakdown request to `sidekick-report`, with six explicitly forbidden inline shortcuts); the `sidekick-find` line routes spanning-recall questions there.
- Sibling skill directories under `skills/` (`sidekick-triage`, `sidekick-checkin`, `sidekick-status`, `sidekick-find`, `sidekick-report`, `sidekick-archive`) are the routing targets.

**Behavior**
- Model-procedure, not executable code: routing is the model recognizing a specialized intent and invoking the corresponding typed skill (a Cowork typed-command hop). This node performs no file writes itself.
- The double-invocation cost of the typed-command hop is accepted by design (Cowork requires the hop); core does not attempt to inline the specialized flows to avoid it.

**Dependencies**
- Upstream: `project-detection/detect-active-project` (the clear-specialized-intent branch).
- Downstream targets are separate skills/flows (`sidekick-triage`, `sidekick-checkin`, `sidekick-status`, `sidekick-find`, `sidekick-report`, `sidekick-archive`); they are invoked, not called as functions.
- The `sidekick-report` route additionally depends on the `sidekick-sync` MCP tools (`build_dashboard`) and `scripts/data.py` for data access, per the hard-rule section.
