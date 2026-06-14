---
domains:
  - surface-gate
edges:
  - label: foreign surface — sidekick-core stands down
    to: surface-gate/core-stand-down
    via: starts
  - label: foreign surface — typed skill refuses
    to: surface-gate/typed-skill-refusal
    via: starts
  - label: guide runs anywhere with a Cowork-only note
    to: surface-gate/guide-anywhere-exception
    via: starts
entry: true
flowId: surface-gate
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/SKILL.md
nodeId: discriminator
parent: sidekick-core/surface-gate
related:
  - sidekick-init/surface-gate-check
  - session-startup/read-settings
slug: discriminator
status: current
summary: The three-way surface classification — sidekick.settings.md present means active workspace, absent with cowork MCP tools means uninitialized Cowork, absent with no cowork tools means foreign surface.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** Classifies the current surface into one of three cases so every Sidekick skill knows whether it may act, offer init, or stand down.
**Inputs:** Presence of `sidekick.settings.md` in the workspace root; availability of Cowork MCP tools (`mcp__cowork__*`).
**Outputs:** One of three verdicts — active Sidekick workspace / uninitialized Cowork (offer `/sidekick-init`) / foreign surface (gate fires).
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** → surface-gate/core-stand-down (starts), → surface-gate/typed-skill-refusal (starts), → surface-gate/guide-anywhere-exception (starts)
**Key rules:**
- `sidekick.settings.md` present = active workspace; act normally.
- Settings absent + Cowork MCP tools present = uninitialized Cowork → offer init, never fabricate settings.
- Settings absent + no Cowork tools = foreign surface → gate fires.
- The settings-file test is read first, before the MCP-tool test.

## Functional (user facing)

### Why use this?
Sidekick is installed at user level, so its skills are loaded everywhere — Cowork, Claude Code, and plain desktop chat alike. The discriminator is the single decision that keeps Sidekick from barging into surfaces where it doesn't belong. The user never invokes it directly; it runs invisibly at the start of any Sidekick skill and decides whether that skill is even allowed to do anything.

### What it does
- Looks for `sidekick.settings.md` in the workspace root as the primary signal of a real Sidekick workspace.
- When that file is present, treats the surface as a live, initialized workspace and lets the skill proceed normally.
- When the file is absent, makes a second check: are Cowork's own MCP tools available in this session?
- If Cowork tools are present but settings are missing, concludes this is a genuine Cowork workspace that simply hasn't been set up yet — the right response is to point the user at `/sidekick-init`, not to invent a configuration.
- If neither the settings file nor Cowork tools are present, concludes this is a foreign surface (a code repo in Claude Code, or a plain chat) and hands off to the gate behaviors.

### When the workspace is uninitialized Cowork
The user is told, once, that they can run `/sidekick-init`, and Sidekick offers to do it. It does not nag on every turn and it never fabricates a settings file to paper over the gap — an empty workspace is a real state, not an error.

### When the surface is foreign
No Sidekick rule is applied. Depending on which skill was entered, one of the three downstream behaviors takes over: the always-on core stands down silently, a typed skill refuses in one line, or the guide explains the plugin with a Cowork-only caveat.

### Behind the scenes
The classification is duplicated by design — it lives as a branch inside `sidekick-core`'s session-start read and as a one-line gate at the top of each typed skill — because each skill is loaded and reasoned about independently and there is no shared runtime to consult. The discriminator is therefore a *pattern* the skills share, not a function they call.

### Pro tips
- The two signals are deliberately different in kind: a file on disk (durable, workspace-scoped) versus a tool availability check (session-scoped). The file wins when present, so an initialized workspace is recognized even if a tool probe is ambiguous.
- A user who wants Sidekick fully inert in a specific code repo can hard-disable the plugin there via `.claude/settings.json` (`enabledPlugins`), independent of this runtime gate.

### Related
- surface-gate/core-stand-down — what the always-on core does on a foreign surface.
- surface-gate/typed-skill-refusal — how the seven typed skills refuse.
- surface-gate/guide-anywhere-exception — the one skill exempt from the refusal.

## Technical

**Main code location**
- `skills/sidekick-core/SKILL.md` — the "Read settings first" section encodes the canonical three-way branch: settings present → load and apply; settings absent + Cowork MCP tools → "workspace isn't initialized" + offer `/sidekick-init`; settings absent + no Cowork tools → stand down silently.

**Signals evaluated**
- `sidekick.settings.md` at the Cowork/workspace root — primary discriminator. Its presence is treated as proof of an active Sidekick workspace (it is written by `/sidekick-init` alongside the root `CLAUDE.md`).
- Availability of `mcp__cowork__*` MCP tools in the session — secondary discriminator, used only when the settings file is absent, to distinguish an uninitialized Cowork workspace from a non-Cowork surface.

**Behavior, not enforcement**
This node describes a model-followed contract, not a runtime guard. Cowork does not fire plugin hooks (SessionStart/PreToolUse are ignored under `--setting-sources user`), so the gate cannot be a hook — it has to be prose the model reads in each skill. The skill descriptions and the `sidekick-sync` MCP server still *load* on every surface; the discriminator gates *behavior*, not loading (the accepted residual cost, see ARCHITECTURE.md §1b).

**Dependencies**
- Downstream within this flow: `surface-gate/core-stand-down`, `surface-gate/typed-skill-refusal`, `surface-gate/guide-anywhere-exception` — the three branches the foreign-surface verdict feeds.
- Spec source: `docs/ARCHITECTURE.md` §1b (Surface gate — Sidekick is Cowork-only).
