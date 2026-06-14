---
flowId: surface-gate
nodeId: typed-skill-refusal
type: process
slug: typed-skill-refusal
status: current
kind: derived
summary: The seven typed skills (init, triage, checkin, archive, status, find, report) refuse in one line on a foreign surface via a Gate blockquote after the H1, saying this is not a Sidekick workspace and stopping.
systems: [skills]
domains: [surface-gate]
parent: sidekick-core/surface-gate
mainCodeFile: skills/sidekick-status/SKILL.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Make each user-invoked typed skill refuse cleanly on a foreign surface instead of running its real flow.
**Inputs:** A typed command (`/sidekick-init|-triage|-checkin|-archive|-status|-find|-report`); the foreign-surface verdict (no `sidekick.settings.md`, no Cowork MCP tools).
**Outputs:** A one-line refusal — "this is not a Sidekick workspace" — and a full stop; no scan, no write, no project access.
**Code anchor:** [skills/sidekick-status/SKILL.md](../../../skills/sidekick-status/SKILL.md)
**Edges:** ← surface-gate/discriminator (starts)
**Key rules:**
- The refusal is a `> **Gate:**` blockquote placed immediately after the skill's H1 — first thing in the body.
- The same gate condition is mirrored in a tail clause on each skill's `description`.
- Seven skills carry the gate; `/sidekick-guide` does not (it is the exception).
- Refuse in one line and stop — do not partially run the flow.

## Functional (user facing)

### Why use this?
The seven typed skills are explicit commands — the user types `/sidekick-status`, `/sidekick-find`, and so on. If the user fires one of these on a surface that isn't a Sidekick workspace (a code repo, a plain chat), they should get an immediate, honest "not here" rather than a half-run command or a confusing error. The gate gives that clean refusal so a mistyped or misplaced command costs nothing.

### What it does
- Covers seven skills: `/sidekick-init`, `/sidekick-triage`, `/sidekick-checkin`, `/sidekick-archive`, `/sidekick-status`, `/sidekick-find`, `/sidekick-report`.
- Each opens with a short gate notice right after its title, before any of its real work.
- On a foreign surface the skill states that this is not a Sidekick workspace and stops — it does not list projects, search, distill, sync, or write anything.
- The same condition is also stated in each skill's description, so the model is discouraged from invoking it on a foreign surface in the first place.

### Foreign surface vs uninitialized workspace
The gate distinguishes two "no settings" situations. With no settings *and* no Cowork tools, the surface is foreign and the skill refuses outright. With no settings but Cowork tools present, the workspace is just uninitialized — the skill instead says the workspace isn't set up and points to `/sidekick-init` (a softer redirect, not a flat refusal).

### Behind the scenes
The refusal is short on purpose. A typed command is a deliberate act, so a one-line "not a Sidekick workspace, stopping" is enough — there's no need to explain the whole gate. This keeps the refusal cheap in both tokens and the user's attention.

### Pro tips
- The seven-skill list is exact: the eighth skill, `/sidekick-guide`, is intentionally left off the gate because it is pure conversation and may explain the plugin anywhere.
- If a typed skill runs its full flow on a foreign surface instead of refusing, suspect a stray `sidekick.settings.md` that is convincing the discriminator this is a real workspace.

### Related
- surface-gate/discriminator — the classification each gate consults.
- surface-gate/core-stand-down — the always-on core's silent equivalent of this refusal.
- surface-gate/guide-anywhere-exception — the one skill deliberately exempt from this gate.

## Technical

**Main code location**
- `skills/sidekick-status/SKILL.md` (and the six siblings: `sidekick-init`, `sidekick-triage`, `sidekick-checkin`, `sidekick-archive`, `sidekick-find`, `sidekick-report`) — each carries the gate as a blockquote directly under its H1, e.g.:
  > **Gate:** no `sidekick.settings.md` and no cowork MCP tools (Claude Code / code repo / plain chat)? Say this isn't a Sidekick workspace and stop.

**Two-layer encoding (matching `sidekick-core`)**
- Body: the `> **Gate:**` blockquote is the in-flow refusal the model reads when the skill is entered.
- Description: each skill's frontmatter `description` ends with a tail clause — e.g. "Cowork Sidekick workspaces only — without sidekick.settings.md and outside Cowork, reply that this is not a Sidekick workspace and stop." — to bias invocation before the body is reached.

**Gate condition**
The blockquote fires on the foreign-surface verdict: no `sidekick.settings.md` **and** no Cowork MCP tools. The skill's own Preconditions section separately handles the missing-settings-but-Cowork case by redirecting to `/sidekick-init` rather than refusing.

**Coverage / consistency**
All seven typed skills share the identical gate wording, keeping the refusal uniform. The structure (blockquote after H1 + description tail) is the repeatable pattern any future typed skill is expected to adopt.

**Dependencies**
- Upstream within this flow: `surface-gate/discriminator` — supplies the foreign-surface verdict.
- Spec source: `docs/ARCHITECTURE.md` §1b — bullet "Typed skills … on a foreign surface they say this is not a Sidekick workspace and stop."
