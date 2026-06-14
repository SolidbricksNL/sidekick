---
flowId: session-startup
nodeId: self-heal-workspace-claude
type: process
slug: self-heal-workspace-claude
status: current
kind: derived
summary: When the workspace-root CLAUDE.md enforcement anchor is missing, offer to recreate it from the init template so Cowork auto-loads the standing rules.
systems: [skills]
domains: [project-model]
parent: sidekick-core/session-startup
mainCodeFile: skills/sidekick-init/references/workspace-claude-template.md
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** On session start, if the workspace-root `CLAUDE.md` enforcement anchor is missing, offer to recreate it from the init template so Cowork re-auto-loads the standing rules.
**Inputs:** trigger = session start after settings are read; checks for `CLAUDE.md` in the workspace root; source = `skills/sidekick-init/references/workspace-claude-template.md`.
**Outputs:** on the user's one-tap yes, the workspace-root `CLAUDE.md` is (re)written from the template; otherwise nothing changes.
**Code anchor:** [skills/sidekick-init/references/workspace-claude-template.md](../../../skills/sidekick-init/references/workspace-claude-template.md)
**Edges:** ← session-startup/read-settings (parent)
**Key rules:**
- Only acts when the anchor is missing — typically an older workspace created before this layer existed.
- Offer once with a single tap; do not nag if declined.
- The anchor is the only reliable always-on surface in Cowork — skills and plugin hooks are not guaranteed to fire.

## Functional (user facing)

### Why use this?
The workspace-root `CLAUDE.md` is what keeps Sidekick's rules in force every single session — it is auto-loaded into the conversation at the start and re-injected after the chat is compacted. If that file is missing (an older workspace set up before this safeguard), the standing rules can silently stop applying. This step quietly notices the gap and offers to fix it, so the workspace keeps protecting itself.

### What it does
- Checks, at session start, whether the workspace root has its `CLAUDE.md` contract file.
- If it is missing, offers — once, with a one-tap choice — to recreate it from the standard template.
- The recreated file restates the hard rules: read your settings, invoke Sidekick, and never leave anything loose in the workspace root — route every write into a project.

### When the anchor is already present
Nothing happens — the file is left exactly as it is and the session continues straight to project detection.

### Behind the scenes
Sidekick's disciplines only bind if the model actually receives them each session. The workspace `CLAUDE.md` is the one mechanism Cowork reliably honours for that, so it carries the standing contract. Setup writes it originally; this step is the self-repair path for workspaces that predate it or had it deleted. The file is kept short on purpose — it loads every session and shares the same size budget as the skills.

### Pro tips
- If you decline, the offer reappears on a later session — it never forces the change.
- This only heals an already-existing workspace once you actually start a session in it; a brand-new workspace gets the file at setup instead.

### Related
- session-startup/read-settings — the parent step; settings are read just before this anchor check.
- session-startup/load-project-context — runs next, picking the active project.

## Technical

**Backing code.** The anchor template `skills/sidekick-init/references/workspace-claude-template.md`, invoked from the session-start protocol in `skills/sidekick-core/SKILL.md` (step 1: if the workspace-root `CLAUDE.md` is missing, offer to create it from the template). `sidekick-init` writes the same file at setup; this node is the `sidekick-core` self-heal path.

**Why an anchor rather than a hook.** Per `docs/ARCHITECTURE.md` §3.0a: a skill (even one labelled always-on) fires only by model invocation, and Cowork does not fire plugin hooks (no SessionStart/PreToolUse; plugin-scoped `hooks.json` is ignored). The one always-on surface Cowork honours is a `CLAUDE.md` in the workspace root, auto-loaded each session and re-injected after compaction — so the hard rules live there.

**Contract carried by the template.** Read `sidekick.settings.md` and apply role/languages; invoke `sidekick-core` and follow its session-start protocol; "nothing loose in the workspace root" — only `sidekick.settings.md` and the `CLAUDE.md` belong loose, the only folders are `projects/`, `_triage/`, `_archive/`; every write routes to `projects/<slug>/{log,brain,output,data}`.

**Constraints.** Acts only when the file is absent (older workspaces). Offered once, one-tap, no nagging. Kept small — subject to the same ~15808 B install/read truncation cliff as the skills. Reaches a given workspace only when a session actually invokes `sidekick-core` there (or the file is placed by hand).

**Dependencies.** Parent `session-startup/read-settings`. Precedes `session-startup/load-project-context` in the protocol order.
