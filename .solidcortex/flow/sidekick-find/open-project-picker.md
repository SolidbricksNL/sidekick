---
flowId: sidekick-find
nodeId: open-project-picker
type: process
slug: open-project-picker
status: current
kind: derived
summary: Only if the user wants to act on a hit, offer through the interactive picker to open that project and hand off to the normal sidekick-core flow — the sole follow-up, writing nothing itself.
systems: [skills]
domains: [project-model, onboarding]
parent: main/sidekick-find
mainCodeFile: skills/sidekick-find/SKILL.md
edges:
  - to: session-startup/read-settings
    via: starts
    label: hand off to open project
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** The single optional follow-up — offers, via the interactive picker, to open a project from the hit list and hand off to the normal sidekick-core flow.
**Inputs:** The ranked hit list from report-hits; the user's wish to act on a specific hit.
**Outputs:** A picker to choose a project; on selection, control passes to session-startup/read-settings. Writes nothing itself.
**Code anchor:** [skills/sidekick-find/SKILL.md](../../../skills/sidekick-find/SKILL.md)
**Edges:** ← sidekick-find/report-hits (parent), → session-startup/read-settings (starts)
**Key rules:**
- Offer only when the user wants to act on a hit — opening a project is the sole follow-up.
- This node writes nothing; the hand-off target runs the normal flow.
- Use the interactive picker for the choice, per the plugin-wide interaction style.

## Functional (user facing)

### Why use this?
Recall often ends with "...and now take me there." Once the results are in front of you, this step lets you jump straight into the project a hit belongs to, without retyping its name or hunting for it — turning a found answer into the start of real work.

### What it does
- Appears only when you actually want to act on a result — it never pushes you into a project on its own.
- Presents the choice as an interactive picker, the same style of menu used everywhere in Sidekick.
- On your pick, opens that project and switches into the normal working flow.
- Does nothing else: it changes no files and makes no other follow-up offers.

### Behind the scenes
This is the one and only door out of recall. Everything before it was read-only lookup; selecting a project here hands you off to the standard project open, exactly as if you'd opened it directly. From that point you're back in the normal Sidekick flow, where edits and actions are allowed again.

### Pro tips
- If you only wanted the answer, just don't pick anything — recall stays read-only and nothing changes.
- Opening from a hit lands you in the same place as opening the project the usual way; there's no special "recall mode" to leave.

### Related
- sidekick-find/report-hits — the ranked list this picker acts on.
- session-startup/read-settings — the normal project-open flow this hands off to.

## Technical

**Main code.** `skills/sidekick-find/SKILL.md`, the tail of the "Output" section and the "Boundaries" section. The skill is a prose-instruction file; this node is the agent offering the optional follow-up after results are shown.

**Trigger & gate.** Offered only when the user signals intent to act on a hit. It is the *only* permitted follow-up to recall — "Opening a project is the only follow-up; everything else stays read-only." The choice is presented through the interactive picker, consistent with the plugin-wide interaction style (`interaction-style.md`).

**Hand-off.** On selection, control passes to `session-startup/read-settings` — the normal project-open flow — which is where writes/actions resume. This node itself persists nothing; per `docs/ARCHITECTURE.md` §11b the whole `sidekick-find` skill is read-only and carries no backup or gatekeeper. The boundary between read-only recall and the writable core flow is exactly this hand-off edge.

**Dependencies.** Parented to `sidekick-find/report-hits` (source of the hit to open). Crosses flows to `session-startup/read-settings`. No Python, no MCP, no file I/O in this node.
