---
domains:
  - onboarding
edges:
  - label: settings read, check anchor
    to: session-startup/self-heal-workspace-claude
    via: starts
  - label: role applied, pick project
    to: session-startup/load-project-context
    via: starts
entry: true
flowId: session-startup
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-core/SKILL.md
nodeId: read-settings
parent: sidekick-core/session-startup
related:
  - surface-gate/discriminator
  - sidekick-init/surface-gate-check
slug: read-settings
status: current
summary: Read sidekick.settings.md at session start, load role plus chat and output languages, and apply role adaptation immediately.
systems:
  - skills
type: process
---

## TLDR (agent)
**Purpose:** First step of every session — read `sidekick.settings.md`, load role plus chat and output languages, and apply them before any work.
**Inputs:** trigger = session start (entry node of session-startup); reads `sidekick.settings.md` in the Cowork workspace root.
**Outputs:** active role, chat language, default output language, connection flags loaded and applied; hands off to anchor check and project detection.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** → session-startup/self-heal-workspace-claude (starts), → session-startup/load-project-context (starts)
**Key rules:**
- Settings present → chat in chat language; deliverables in default output language unless asked otherwise; adopt the role.
- Settings missing AND Cowork (cowork MCP tools present) → tell the user once they can run `/sidekick-init`, offer it, never fabricate settings.
- Settings missing AND any other surface (Claude Code, code repo, plain chat) → stand down silently, apply no rule, don't touch `projects/`.

## Functional (user facing)

### Why use this?
This is the moment Sidekick learns who you are and how to talk to you. Reading your settings up front means it speaks your language, writes deliverables in the right output language, and shapes its tone and advice to your role — without you re-stating any of that each session.

### What it does
- Reads the one settings file in the workspace root at the very start of the conversation, before any project work.
- Loads four things: your role, the language Sidekick chats in, the language it writes deliverables in by default, and which connections (email, etc.) are on.
- Applies role adaptation immediately — tone, focus, and the kind of advice it gives are tuned to your role for the rest of the session.
- Drives the surface gate: a workspace with a settings file is a live Sidekick workspace; one without it is either an uninitialized Cowork workspace or a foreign surface.

### When the settings file is missing
Sidekick branches on where it is running. Inside Cowork (it can tell from the Cowork tools being available) the workspace simply hasn't been set up yet — it lets you know, once, that `/sidekick-init` will set it up and offers to run it. Anywhere else — Claude Code, a code repository, an ordinary chat — it stays completely silent and behaves as if the plugin weren't installed.

### Behind the scenes
The settings file is the single record of your preferences; it is written and edited only by the setup skill, never invented on the fly. If it is absent, Sidekick never guesses values — it either offers setup or stands down, depending on the surface.

### Pro tips
- Change your role, chat language, or output language by re-running setup; this step picks the change up on the next session.
- If Sidekick ever seems to ignore your role or language, the settings file is the place that drives it.

### Related
- session-startup/self-heal-workspace-claude — repairs the always-on workspace contract once settings are read.
- session-startup/load-project-context — picks the active project after role and languages are applied.

## Technical

**Backing code.** Session-start protocol and the "Read settings first" section of `skills/sidekick-core/SKILL.md`. This is the `entry: true` node of the `session-startup` subflow.

**Settings file.** `sidekick.settings.md` in the Cowork workspace root (the directory holding the workspace `CLAUDE.md`). Fields consumed: role (free text), chat language, default output language, and connection flags. Written exclusively by `sidekick-init` (`docs/ARCHITECTURE.md` §8); this node only reads it.

**Surface discrimination.** Presence of `sidekick.settings.md` marks an active workspace. Absence is disambiguated by whether Cowork MCP tools are available: present ⇒ uninitialized Cowork (offer `/sidekick-init`); absent ⇒ foreign surface ⇒ `sidekick-core` stands down silently. This is the runtime half of the surface gate (`docs/ARCHITECTURE.md` §1b / §3.0a); the description-level gate forbids invocation outside Cowork.

**Application.** Role/chat-language/output-language are applied for the remainder of the session: chat in chat language, deliverables in output language unless overridden, role tunes tone and advice (optionally drawing on a role-specific skill, never depending on one).

**Dependencies.** Followed by `session-startup/self-heal-workspace-claude` (anchor repair) and `session-startup/load-project-context` (project detection), both reached once settings are read and role is applied.
