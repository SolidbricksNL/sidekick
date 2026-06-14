---
flowId: sidekick-guide
nodeId: entry-picker
type: process
slug: entry-picker
status: current
kind: derived
summary: Multiple-choice entry point — full guided tour, jump to one skill, just the principle, or exit — routing the user into the rest of the flow.
systems: [skills]
domains: [onboarding]
parent: main/sidekick-guide
mainCodeFile: skills/sidekick-guide/SKILL.md
edges:
  - to: sidekick-guide/guided-tour
    via: starts
    label: full tour or jump-to-skill
  - to: sidekick-guide/recap-next-step
    via: starts
    label: just-the-principle or exit
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Ask one multiple-choice question — how the user wants to explore Sidekick — and route to the matching path.
**Inputs:** User arriving from the principle opener; one picker selection.
**Outputs:** Route to guided tour (full or jump-to-skill), or to the recap (just-the-principle / exit).
**Code anchor:** [skills/sidekick-guide/SKILL.md](../../../skills/sidekick-guide/SKILL.md)
**Edges:** → sidekick-guide/guided-tour (starts), → sidekick-guide/recap-next-step (starts)
**Key rules:**
- Always an interactive tappable picker, never a typed-text list.
- Exactly four options; full guided tour is the default.
- Option labels are translated to the chat language at render time.

## Functional (user facing)

### Why use this?
Not everyone needs the same thing from the guide. A first-timer wants the full walk-through; someone who only forgot what one command does wants to jump straight to it; someone who already gets the big picture just wants the wrap-up. This single question puts you on the right path in one tap.

### What it does
- Asks one question — "How do you want to explore Sidekick?" — and waits for your pick.
- Offers four routes:
  - **Full tour** — walk every skill, group by group (this is the default).
  - **Jump to a specific skill** — pick one and read just that entry.
  - **Just the principle** — you've got the big picture; skip ahead to the wrap-up.
  - **I've seen enough** — exit cleanly with the recap.
- Sends you down the chosen path; nothing is decided for you beyond where to go next.

### How it connects

```text
                          ┌─ Full tour ──────────┐
Open principle → Entry ──┼─ Jump to a skill ─────┤→ Guided tour
              picker     ├─ Just the principle ──┐
                          └─ I've seen enough ────┴→ Recap + next step
```

### Behind the scenes
The two "tour" choices (full and jump-to-skill) both lead into the same guided-tour step, which then behaves differently depending on which you picked. The two "I'm done" choices (just-the-principle and exit) skip straight to the recap. Either way nothing is written and nothing is scanned — it is purely a routing question.

### Pro tips
- The labels appear in your own language, but they map to the same four routes underneath.
- Choosing "just the principle" still ends with the recap, so you won't miss the next-step nudge.

### Related
- sidekick-guide/open-principle — the opener shown immediately before this.
- sidekick-guide/guided-tour — where the two tour options lead.
- sidekick-guide/recap-next-step — where the two finish-up options lead.

## Technical

- **`skills/sidekick-guide/SKILL.md`** — "Flow → 2. Entry picker" defines the single question and its four options, with the full guided tour marked as default.
- **Routing** — the "full tour" and "jump to a specific skill" options both enter `sidekick-guide/guided-tour` (which branches on the chosen mode per the SKILL's step 3 vs. step 4); "just the principle" and "I've seen enough" both enter `sidekick-guide/recap-next-step`.
- **Interaction contract** — per SKILL.md and `skills/sidekick-core/references/interaction-style.md`, every choice point is the interactive picker; this step must not degrade to a typed-text list.
- **Localization** — option labels (authored in Dutch/English in the register-aligned SKILL flow) are translated to the chat language at render time; the route each maps to is fixed.
- **No side effects** — no Bash, writes, or scans; the picker only selects an in-flow branch.
