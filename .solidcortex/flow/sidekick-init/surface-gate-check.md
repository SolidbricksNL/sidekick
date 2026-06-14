---
domains:
  - surface-gate
  - onboarding
edges:
  - label: surface ok → ask
    to: sidekick-init/run-questionnaire
    via: starts
flowId: sidekick-init
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-init/SKILL.md
nodeId: surface-gate-check
parent: main/sidekick-init
related:
  - surface-gate/discriminator
  - session-startup/read-settings
slug: surface-gate-check
status: current
summary: Precondition that refuses init outside a real Cowork surface and detects whether the workspace is already set up before the questionnaire runs.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** Gate init to a real Cowork surface, then check whether the workspace is already set up before any questionnaire runs.
**Inputs:** trigger=`/sidekick-init` (or missing settings / "set up workspace"); presence of cowork MCP tools; presence of `sidekick.settings.md` in the Cowork root.
**Outputs:** stop+message outside Cowork; OR re-configure/keep prompt when settings exist; OR pass-through to the questionnaire.
**Code anchor:** [skills/sidekick-init/SKILL.md](../../../skills/sidekick-init/SKILL.md)
**Edges:** → sidekick-init/run-questionnaire (surface ok → ask)
**Key rules:**
- No cowork MCP tools present → say Sidekick workspaces are set up in Cowork, and stop.
- `sidekick.settings.md` already in root → do not silently overwrite; offer re-configure vs keep and proceed only on a clear answer.
- When chat language is not yet known, ask it first and switch into it before anything else.

## Functional (user facing)

### Why use this?
This is the doorway to setup. It makes sure you are in the right place (a Cowork workspace) before asking you anything, and it protects an already-configured workspace from being wiped by accident. You normally never see it as a separate step — it just decides what happens when you start setup.

### What it does
- Confirms you are inside Cowork. Outside Cowork (for example in a plain code editor) it does nothing except tell you that Sidekick workspaces are created in Cowork.
- Looks for an existing settings file in your workspace root.
- If none exists, it hands straight over to the setup questions.
- If one already exists, it shows you a short summary of your current setup and asks whether you want to re-configure (run the questions again and overwrite) or keep what you have.

### When the workspace is already set up
You get a recap of your current role, languages, and connections, and a simple choice. Picking "keep" leaves everything untouched. Picking "re-configure" starts the questions over and will overwrite your settings once you confirm at the end.

### When the chat language is unknown
On a brand-new workspace there are no saved preferences yet, so the very first thing asked is which language to talk in. From that point on, the rest of setup happens in your chosen language.

### Behind the scenes
The check reads only the settings file to make its decision — it writes nothing. Persisting anything is left to the later steps, after you confirm.

### Pro tips
- Re-running `/sidekick-init` on an existing workspace is safe: it always asks before overwriting.
- If you started in the wrong app, the gate message is your cue to move into Cowork and try again.

### Related
- [sidekick-init/run-questionnaire](run-questionnaire.md) — the setup questions this gate hands off to.

## Technical

**Main code locations**
- `skills/sidekick-init/SKILL.md` — the gate blockquote after the H1 (`> **Gate:** not in Cowork…`), the description tail (Cowork-only refusal), and the "Before you start" section that drives the existing-settings branch and the language-first rule.
- `commands/sidekick-init.md` — `/sidekick-init` entry that invokes the skill.

**Surface discrimination.** The gate keys off the presence of cowork MCP tools at runtime: absent ⇒ foreign surface ⇒ refuse and stop. This is part of the plugin-wide surface gate (ARCHITECTURE §1b): the skill description forbids invocation on foreign surfaces and the gate blockquote is the in-body backstop. The discriminator between an active workspace and an uninitialized-but-valid Cowork is `sidekick.settings.md` — present ⇒ already set up; absent ⇒ run setup.

**State touched.** Read-only: the existence and contents of `sidekick.settings.md` in the Cowork root. No writes occur in this node; all persistence is downstream (`write-settings`, `write-workspace-claude`).

**Dependencies.** Hands off to `sidekick-init/run-questionnaire` once the surface check passes and the user has cleared any existing-settings prompt. Upstream trigger is the `/sidekick-init` command or a session in which `sidekick.settings.md` is missing.
