---
flowId: surface-gate
nodeId: guide-anywhere-exception
type: process
slug: guide-anywhere-exception
status: current
kind: derived
summary: sidekick-guide is the gate exception — pure conversation that may explain the plugin anywhere, but outside Cowork it notes up front that Sidekick itself only operates in a Cowork workspace.
systems: [skills]
domains: [surface-gate, onboarding]
parent: sidekick-core/surface-gate
mainCodeFile: skills/sidekick-guide/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Let `sidekick-guide` explain the plugin on any surface — the single exception to the surface gate — while still flagging that Sidekick only *operates* in Cowork.
**Inputs:** `/sidekick-guide` (or a "how does Sidekick work" intent) on any surface; the surface check (are Cowork MCP tools present?).
**Outputs:** A full explanation either way; outside Cowork, a one-line up-front caveat that Sidekick itself runs only in a Cowork workspace, then the explanation proceeds.
**Code anchor:** [skills/sidekick-guide/SKILL.md](../../../skills/sidekick-guide/SKILL.md)
**Edges:** ← surface-gate/discriminator (starts)
**Key rules:**
- The guide never refuses — it explains everywhere because it is pure conversation.
- Outside Cowork it states up front that Sidekick only operates in a Cowork workspace, then explains.
- It reads only `sidekick.settings.md` (for chat language) and writes nothing — safe before `/sidekick-init`.
- It is the only typed skill exempt from the one-line foreign-surface refusal.

## Functional (user facing)

### Why use this?
Someone who has just encountered Sidekick — possibly in a code repo or a plain chat, before they've ever opened a Cowork workspace — should be able to ask "what is this and how does it work?" and get a real answer. If the guide refused like the other typed skills, a first-time user would be locked out of the very explanation that tells them where Sidekick belongs. So the guide is deliberately carved out of the gate: it talks anywhere.

### What it does
- Runs on any surface, including outside Cowork, without refusing.
- Outside Cowork it opens with a brief, honest note that Sidekick *itself* only operates inside a Cowork workspace — then goes on to explain the plugin fully.
- Inside Cowork it simply explains, with no caveat needed.
- Reads only `sidekick.settings.md` (to pick up the chat language) and touches nothing else — it works fine on a fresh, un-initialized workspace before `/sidekick-init` has ever run.

### When outside Cowork
The user still gets the complete walk-through — the core principle and the per-skill tour — but with the expectation set correctly: the explanation is portable, the *behavior* is not. This prevents the user from trying to run, say, `/sidekick-status` in a code repo and being surprised when it refuses.

### Behind the scenes
The guide is the safe-everywhere skill precisely because it is read-only and write-free. It never scans projects, never syncs, never creates files. That is what makes relaxing the gate harmless here: even on a foreign surface there is nothing it can do that the gate exists to prevent.

### Pro tips
- This is the right skill to point a curious newcomer at regardless of where they are — it's the only one guaranteed not to refuse.
- The "Sidekick only operates in Cowork" caveat is a courtesy, not a restriction: the guide will still answer every question; it just sets honest expectations first.

### Related
- surface-gate/discriminator — supplies the surface signal the guide checks before deciding whether to add the caveat.
- surface-gate/typed-skill-refusal — the gate behavior the guide is exempt from.

## Technical

**Main code location**
- `skills/sidekick-guide/SKILL.md` — instead of the typed skills' refusal blockquote, it carries a **Surface note** blockquote after its H1:
  > **Surface note:** you may run anywhere (pure conversation), but outside Cowork (no cowork MCP tools) say up front that Sidekick itself only operates in a Cowork workspace — then explain away.
- Its `description` ends with the matching clause: "Pure conversation, so it may answer anywhere — but outside Cowork, note that Sidekick itself only operates in Cowork workspaces."

**Why the exception is safe**
The guide is explicitly read-only and write-free: it reads `sidekick.settings.md` only for chat language and never writes, scans, or touches project data. Because it cannot perform any of the workspace mutations the gate is designed to suppress, lifting the gate for it carries no risk — the surface note is purely about setting user expectations, not about guarding behavior.

**Surface signal**
The caveat branch keys on the same "are Cowork MCP tools present?" check used by the discriminator: tools present → inside Cowork, no caveat; tools absent → outside Cowork, prepend the one-line caveat. Unlike the typed skills, the absence of `sidekick.settings.md` does not change whether the guide runs — only whether the caveat is shown.

**Content boundary**
The guide's substantive content (core principle + per-skill blurbs) lives in `skills/sidekick-guide/references/skill-register.md`, not in this gate logic; this node concerns only the run-anywhere exception, not the onboarding flow itself.

**Dependencies**
- Upstream within this flow: `surface-gate/discriminator` — the surface classification whose Cowork-tools signal the caveat branch reuses.
- Spec source: `docs/ARCHITECTURE.md` §1b — "`/sidekick-guide` is the exception — pure conversation, it may explain the plugin anywhere, but notes that Sidekick itself only operates in Cowork."
