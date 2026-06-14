---
flowId: surface-gate
nodeId: core-stand-down
type: process
slug: core-stand-down
status: current
kind: derived
summary: On a foreign surface sidekick-core stands down silently — its description forbids invocation and its Read-settings-first step applies no Sidekick rule, makes no init offer, and touches no projects.
systems: [skills]
domains: [surface-gate]
parent: sidekick-core/surface-gate
mainCodeFile: skills/sidekick-core/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Make the always-on `sidekick-core` skill behave as if uninstalled when the surface is foreign, so it never imposes workspace rules outside Cowork.
**Inputs:** A foreign-surface verdict from the discriminator (no `sidekick.settings.md`, no Cowork MCP tools); the skill's own description; its "Read settings first" branch.
**Outputs:** Total inaction — no Sidekick rule applied, no `/sidekick-init` offer, no `projects/` access; the session looks plugin-free.
**Code anchor:** [skills/sidekick-core/SKILL.md](../../../skills/sidekick-core/SKILL.md)
**Edges:** ← surface-gate/discriminator (starts)
**Key rules:**
- The description forbids model-invocation outside a Sidekick workspace — the first line of defense.
- On a foreign surface: no Sidekick rule, no init offer, no `projects/` touch.
- Stand-down is silent — the skill does not announce that it is standing down.
- `sidekick-core` is the only model-invoked skill, so it is the only one that needs this branch (vs the typed skills' explicit refusal).

## Functional (user facing)

### Why use this?
`sidekick-core` is the always-on layer — the model reaches for it whenever real work starts. That's exactly what you want inside a Cowork workspace and exactly what you don't want in a code repo or a casual chat, where it would otherwise try to anchor everything in projects and enforce write disciplines that make no sense there. Stand-down is the value: outside Cowork the user gets a normal, un-opinionated assistant, as if Sidekick weren't installed at all.

### What it does
- Refuses to engage twice over: first the skill's description tells the model not to invoke it outside a Sidekick workspace at all; second, if it is invoked anyway, the "Read settings first" branch routes straight to stand-down.
- Applies no write disciplines, no project model, and no role-adaptation on a foreign surface.
- Does not list, read, or create anything under `projects/`.
- Makes no `/sidekick-init` offer — that offer is reserved for genuine but uninitialized Cowork workspaces, which a foreign surface is not.

### When the workspace is real but uninitialized
The same "Read settings first" branch handles the adjacent case differently: in Cowork with no settings yet, the user is told once they can run `/sidekick-init` and is offered help. Stand-down applies only to the *foreign* branch — the absence of both the settings file and Cowork tools.

### Behind the scenes
The silence is deliberate. Announcing "Sidekick is standing down" would itself be Sidekick behavior leaking onto a surface where the plugin is meant to be invisible. So the skill simply does nothing Sidekick-specific and lets the underlying assistant answer normally.

### Pro tips
- Because this is the *only* model-invoked skill, it is the only place a silent stand-down is needed — the user never types it, so it can't put up a refusal banner the way a typed command does.
- If `sidekick-core` ever does act on a foreign surface, the root cause is almost always a stale or misplaced `sidekick.settings.md` making the discriminator believe it's in a real workspace.

### Related
- surface-gate/discriminator — the classification that produces the foreign-surface verdict this node consumes.
- surface-gate/typed-skill-refusal — the parallel behavior for the user-invoked typed skills.

## Technical

**Main code location**
- `skills/sidekick-core/SKILL.md` — two cooperating mechanisms:
  - The `description` frontmatter: states the skill is for "ONLY in a Cowork Sidekick workspace … NEVER in Claude Code, a code repo, or any other session — there the plugin is inert." This steers the model's invocation decision before the skill body is ever entered.
  - The "Read settings first" section: when `sidekick.settings.md` is absent it branches on surface — "**Anywhere else** (Claude Code, a code repo, a plain chat) **stand down silently** — apply no Sidekick rule, don't offer `/sidekick-init`, don't touch `projects/`; act as if the plugin weren't installed."

**Why a branch and not a hook**
Cowork does not fire plugin hooks, and `sidekick-core` is "always-on" only by model-invocation, not by a runtime trigger. The stand-down therefore has to be encoded as model-readable prose in the skill itself; there is no SessionStart/PreToolUse guard to fall back on.

**Scope of the stand-down**
The skill suppresses its own session-start protocol (settings read → project detection → project CLAUDE.md read → `reconcile_output` → work). None of those steps run on a foreign surface.

**Dependencies**
- Upstream within this flow: `surface-gate/discriminator` — supplies the foreign-surface verdict.
- Spec source: `docs/ARCHITECTURE.md` §1b — bullet "`sidekick-core` (the only model-invoked skill): … on a foreign surface it stands down silently."
