---
flowId: sidekick-guide
nodeId: guided-tour
type: process
slug: guided-tour
status: current
kind: derived
summary: Walk the register's skill groups (or one jumped-to skill) with a per-group check-in picker — continue, tell more, free-text question answered only from the register, or stop.
systems: [skills]
domains: [onboarding]
parent: main/sidekick-guide
mainCodeFile: skills/sidekick-guide/references/skill-register.md
edges:
  - to: sidekick-guide/recap-next-step
    via: starts
    label: tour done or stopped
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Walk the register's skill groups (or one jumped-to skill), rendering each entry with a per-step check-in picker.
**Inputs:** Mode from entry picker (full tour or jump-to-skill); the register's groups/entries; per-step picker choices and optional free-text questions.
**Outputs:** Skills rendered group-by-group; routes to the recap when the tour is done or stopped.
**Code anchor:** [skills/sidekick-guide/references/skill-register.md](../../../skills/sidekick-guide/references/skill-register.md)
**Edges:** → sidekick-guide/recap-next-step (starts)
**Key rules:**
- Render only register fields (`title`/`command`/`blurb`, plus `when`/`triggers` on "tell me more"); invent nothing.
- Free-text questions are answered only from the register; if nothing matches, say so and point back to the tour.
- A check-in picker follows every group; all pickers are interactive, never typed lists.
- "Tell me more" and "I have a question" re-offer the same check-in rather than advancing.

## Functional (user facing)

### Why use this?
This is the heart of the tour — where you actually learn what each skill does and when to reach for it. It moves at your pace: after every group you decide whether to go deeper, ask something, or move on. Nothing is dumped on you in one wall of text.

### What it does
- On the **full tour**, walks the seven groups in order: the basis (the always-on engine), getting set up, presenting your work, keeping overview, not missing anything, finishing/cleaning up, and finally this guide itself.
- For each skill in a group it shows the skill's title, its command, and a short blurb of what it is for.
- After each group it pauses with a check-in offering four choices:
  - **Clear, next** — move on to the next group.
  - **Tell me more** — also show, for every skill in the group, when to use it and what triggers it; then ask the same check-in again.
  - **I have a question** — type a free-text question and get it answered from what the guide knows about the skills; then ask the same check-in again.
  - **Stop the tour** — jump to the wrap-up.
- On the **jump-to-a-skill** path it instead shows a picker of all skills, reads the full entry for the one you choose, then lets you pick another, start the full tour, or finish.

### When you ask a free-text question
The guide answers only from what it actually knows about the skills — it matches your question to the most relevant skill and reads that out. If nothing fits, it tells you plainly rather than guessing, and points you back to the tour.

### Behind the scenes
Everything the guide says about a skill comes from a single content source it renders word for word. It does not improvise descriptions, so two people taking the tour hear the same thing. Because it only reads that content and your settings, it never looks at your projects or writes anything.

### Pro tips
- Use "Tell me more" on a group only when a skill there is relevant to you — otherwise "Clear, next" keeps the tour short.
- The jump-to path is the fast lane when you just need to remember one command.
- A long skill list is split across two picker prompts so the options stay tappable.

### Related
- sidekick-guide/entry-picker — chooses between the full tour and the jump-to path that feed this step.
- sidekick-guide/recap-next-step — where the tour lands when it finishes or you stop it.

## Technical

- **`skills/sidekick-guide/references/skill-register.md`** — the single content source. The `## Tour order (groups)` section fixes the seven-group order (`basis → setup → present → overview → stay-on-top → housekeeping → guide`); the `## Register` YAML block holds one entry per skill (`slug`, `group`, `title`, `command`, `blurb`, `when`, `triggers`).
- **`skills/sidekick-guide/SKILL.md`** — "Flow → 3. Guided tour" drives the full-tour loop (render `title`/`command`/`blurb` per skill, then the check-in; "tell me more" additionally renders `when`/`triggers`); "Flow → 4. Jump path" drives the single-skill picker. Anti-hallucination is enforced here: render the register verbatim, never expand a blurb.
- **Free-text Q&A** — bounded strictly to the register: match the question to the most relevant skill entry and read its fields; on no match, state so and return to the check-in. No external lookup, no web, no project scan.
- **Picker batching** — the jump-path skill picker is split across two questions when the skill count exceeds a single four-option prompt.
- **Interaction contract** — all check-ins and menus use the interactive picker per `skills/sidekick-core/references/interaction-style.md`; "tell me more" and "I have a question" re-offer the same check-in instead of advancing.
- **Drift guard** — `scripts/validate-structure.mjs` Check 8 fails CI if any `skills/*` folder lacks a register entry, so this tour can never silently omit a skill.
- **No side effects** — pure conversation; no Bash, subagents, `data.py`, writes, or scans.
