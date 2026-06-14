---
flowId: sidekick-guide
nodeId: open-principle
type: process
slug: open-principle
status: current
kind: derived
summary: Read sidekick.settings.md for the chat language and render the register's core-principle opener (projects + the three write disciplines).
systems: [skills]
domains: [onboarding, write-disciplines]
parent: main/sidekick-guide
mainCodeFile: skills/sidekick-guide/SKILL.md
entry: true
edges:
  - to: sidekick-guide/entry-picker
    via: starts
    label: offer how-to-explore choices
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Open the guide by reading the chat language and rendering the register's core-principle section verbatim.
**Inputs:** `/sidekick-guide` invocation or onboarding intent; `sidekick.settings.md` (optional — for chat language).
**Outputs:** Rendered Core-principle opener (two ideas + disciplines table); hands off to the entry picker.
**Code anchor:** [skills/sidekick-guide/SKILL.md](../../../skills/sidekick-guide/SKILL.md)
**Edges:** → sidekick-guide/entry-picker (starts)
**Key rules:**
- Content comes only from the register's `Core principle` section — never invented or embellished.
- Reads at most `sidekick.settings.md`; no other file, no write, no scan.
- Runs on an un-initialized workspace; missing settings is fine — default to English, never refuse.

## Functional (user facing)

### Why use this?
This is the first thing the guide says. Before listing any commands, it tells you the one idea the whole plugin is built on, so every skill you meet afterwards makes sense in context. If you are new to Sidekick, this is where you start.

### What it does
- Greets you in your own language (one or two lines of welcome if you are clearly new), then lays out the principle.
- Explains the **two ideas**: every piece of work lives in a project folder with a fixed shape, and three write disciplines decide where things go and who approves them.
- Shows the small disciplines table at a glance: process notes go to the logbook freely, distilled knowledge into the brain with your approval, deliverables and structured data only on your confirmation.
- Frames the rest of the tour: every skill is built on these two ideas.

### How it connects

```text
/sidekick-guide → Open with the principle (this) → Entry picker
```

### Behind the scenes
The guide picks up your chat language from your saved settings if they exist. On a brand-new workspace those settings won't be there yet — that is completely normal for a first-time user, and the guide simply speaks your apparent language (English by default) and carries on. It never stops to make you set anything up first.

### Pro tips
- You can run this before doing any setup — it is the one safe-anywhere starting point.
- It reads nothing about your actual projects, so there is no risk of it touching your work.

### Related
- sidekick-guide/entry-picker — the choice of how to explore, shown right after this.
- sidekick-guide/recap-next-step — where "just the principle" lands you.

## Technical

- **`skills/sidekick-guide/SKILL.md`** — "Flow → 1. Open with the principle" orchestrates this step: render the **Core principle** section from the register, keep to its wording, optionally prefix one or two welcome sentences.
- **`skills/sidekick-guide/references/skill-register.md`** — `## Core principle (the tour opener)` is the canonical English content rendered here, including the disciplines markdown table (log / brain / output / data with their gatekeepers).
- **Language resolution** — reads `sidekick.settings.md` for the chat language when present; falls back to the user's apparent language, defaulting to English, when it is absent. Only the surface text is translated; the register's meaning is canonical.
- **No-write contract** — per SKILL.md "Boundaries", this node performs no Bash, subagents, `data.py`, scans, or filesystem writes; the sole file read is `sidekick.settings.md`.
- **Entry node** — `entry: true`; this is the first node reached on `/sidekick-guide`. It unconditionally hands off to `sidekick-guide/entry-picker`.
