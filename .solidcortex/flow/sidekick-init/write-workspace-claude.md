---
flowId: sidekick-init
nodeId: write-workspace-claude
type: process
slug: write-workspace-claude
status: current
kind: derived
summary: Writes the workspace-root CLAUDE.md enforcement anchor verbatim from the template — the always-on contract Cowork auto-loads to keep every future session structured.
systems: [skills]
domains: [write-disciplines, onboarding]
parent: main/sidekick-init
mainCodeFile: skills/sidekick-init/references/workspace-claude-template.md
edges:
  - to: sidekick-init/scaffold-first-project
    via: starts
    label: then scaffold project
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Write the workspace-root `CLAUDE.md` enforcement anchor verbatim from the template — the always-on contract Cowork auto-loads every session.
**Inputs:** template `references/workspace-claude-template.md` (no placeholders); existing root `CLAUDE.md` if any.
**Outputs:** `CLAUDE.md` at the Cowork root carrying the "nothing loose in the root" standing orders.
**Code anchor:** [skills/sidekick-init/references/workspace-claude-template.md](../../../skills/sidekick-init/references/workspace-claude-template.md)
**Edges:** → sidekick-init/scaffold-first-project (then scaffold project)
**Key rules:**
- Copy the template verbatim — there are no placeholders to fill.
- If a root `CLAUDE.md` already exists, show its content and ask before overwriting.
- This anchor (not the always-on skill) is what reliably keeps later sessions structured, because Cowork does not fire plugin hooks.

## Functional (user facing)

### Why use this?
This step lays down the house rules for your workspace. Cowork reads this file at the start of every chat (and again after a long conversation is compacted), so these rules are always in force — even in sessions where Sidekick's main skill doesn't announce itself. Without it, stray notes and files would pile up at the top of your workspace.

### What it does
- Writes a short rules file to the top of your workspace.
- States the one hard rule: nothing loose in the root — every document, note, draft, or data file belongs to a project.
- Tells future sessions to read your settings first and then enter the right project before doing any work.
- Routes each kind of work to the right place: drafts to a project's working area, distilled knowledge to its brain, deliverables to its output, structured data to its data store.

### When a CLAUDE.md already exists
If your workspace root already has one of these files, Sidekick shows you what's there and asks before replacing it, so a hand-written or pre-existing file is never silently clobbered.

### Behind the scenes
The content is fixed — it is copied as-is, with nothing to fill in. That is deliberate: the rules are the same for every Sidekick workspace, and keeping them identical is what makes them dependable.

### Pro tips
- If structure ever drifts, this file is the thing that pulls a session back into line — it is re-loaded automatically, so you don't have to remind Sidekick.
- You generally never need to edit it; it is the standing contract, not a per-project setting.

### Related
- [sidekick-init/write-settings](write-settings.md) — the settings file written just before this one.
- [sidekick-init/scaffold-first-project](scaffold-first-project.md) — the next step, which creates your first project.

## Technical

**Main code locations**
- `skills/sidekick-init/references/workspace-claude-template.md` — the verbatim source: "Before doing any work" (read settings, invoke `sidekick-core`), the hard rule "nothing loose in the workspace root" with the four routing targets (`log/`, `brain/`, `output/`, `data/`), and the projects/areas model.
- `skills/sidekick-init/SKILL.md` — the write step (file 2 of 2) including the "show existing, ask before overwrite" guard.

**Output file.** `CLAUDE.md` at the Cowork root. This is the enforcement anchor introduced in v0.20.0 and is the only reliably always-on surface on Cowork: Cowork auto-loads root `CLAUDE.md` every session and re-injects it after compaction, whereas plugin hooks (SessionStart/PreToolUse, plugin `hooks.json`) are ignored under `--setting-sources user` — so a hook-based always-on rule is a non-starter on Cowork. The standing rules therefore live in this file, not in a hook.

**Self-heal relationship.** `sidekick-core`'s session-start protocol self-heals this file if it is missing, but only once a chat invokes the core skill; init placing it here is the primary path. An already-broken workspace heals only on reinstall reach or a hand-placed file.

**Write discipline.** Verbatim copy, no templating. The only branch is the pre-existing-file guard (show + confirm). It carries `write-disciplines` because it encodes the routing rules that every later write obeys.

**Dependencies.** Upstream: `sidekick-init/write-settings`. Downstream: `sidekick-init/scaffold-first-project`. External: relies on Cowork's auto-load-and-reinject behavior for root `CLAUDE.md` (ARCHITECTURE enforcement-anchor notes).
