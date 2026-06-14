---
flowId: sidekick-guide
nodeId: recap-next-step
type: process
slug: recap-next-step
status: current
kind: derived
summary: Close with a one-line principle-and-groups recap and a next-step picker — start /sidekick-init on a fresh workspace, begin a project, ask another skill question, or end.
systems: [skills]
domains: [onboarding]
parent: main/sidekick-guide
mainCodeFile: skills/sidekick-guide/SKILL.md
edges:
  - to: sidekick-init/surface-gate-check
    via: starts
    label: nudge to first-time setup
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Close the guide with a one-line recap and a next-step picker tailored to whether the workspace is set up.
**Inputs:** Arrival from the entry picker (just-the-principle/exit) or end of the tour; presence/absence of `sidekick.settings.md`.
**Outputs:** Prose recap (principle + group map) and a final picker; can nudge to `/sidekick-init`, hand back to `sidekick-core`, loop to a question, or end.
**Code anchor:** [skills/sidekick-guide/SKILL.md](../../../skills/sidekick-guide/SKILL.md)
**Edges:** → sidekick-init/surface-gate-check (starts)
**Key rules:**
- If `sidekick.settings.md` is missing, `/sidekick-init` is the first, recommended option.
- "Begin a project" hands back to the always-on `sidekick-core`; the guide itself starts nothing and writes nothing.
- "Another question" reuses the tour's register-only Q&A, then re-offers this recap.
- The final picker is interactive, never a typed list.

## Functional (user facing)

### Why use this?
Every way through the guide ends here, so you always leave with the same two things: a one-line reminder of what Sidekick is about, and a concrete suggestion for what to do next. You are never left wondering "okay, now what?"

### What it does
- Gives a short prose recap: the principle in one line, and a one-line map of the skill groups.
- Then offers a final picker — "What do you want to do now?" — whose options adapt to your situation:
  - **Start `/sidekick-init`** — if your workspace isn't set up yet, this is the first and recommended choice.
  - **Begin a project** — if you're already set up, jump into real work.
  - **Another question about a skill** — go back to free-text questions, then return here.
  - **Done** — end warmly.

### When the workspace is fresh
If you haven't run setup yet, the recap recognizes it and puts `/sidekick-init` at the top as the recommended next step — onboarding is exactly the moment before setup, so the guide closes the loop by pointing you there.

### When the workspace is already set up
The recap instead offers to start a real project, which hands you off to the always-on engine that runs your actual work. The guide never starts that work itself.

### Behind the scenes
Whether to recommend setup or starting a project comes down to one thing: whether your settings file exists. The guide checks for it but changes nothing — choosing setup or a project is what triggers the next skill; the guide just opens the door.

### Pro tips
- "Another question" loops you back to the same Q&A as the tour, then drops you here again — handy for clearing up a couple of last doubts before you start.
- Reaching this recap doesn't commit you to anything; "Done" is always a clean exit.

### Related
- sidekick-guide/entry-picker — the just-the-principle and exit choices route straight here.
- sidekick-guide/guided-tour — the tour ends here, and the "another question" option reuses its register-only Q&A.
- sidekick-init/surface-gate-check — where the "start setup" nudge leads on a fresh workspace.

## Technical

- **`skills/sidekick-guide/SKILL.md`** — "Flow → 5. Recap + next step" defines the prose recap (principle one-liner + group map) and the final adaptive picker.
- **Adaptive first option** — the picker branches on the presence of `sidekick.settings.md`: absent → `/sidekick-init` is the first, recommended option (edge to `sidekick-init/surface-gate-check`); present → offer "begin a project," which hands control to the always-on `sidekick-core` skill.
- **Looping Q&A** — "another question about a skill" reuses step 3's register-only question handling (match to the most relevant register entry, answer from it, no invention), then re-offers this same recap.
- **Convergence** — this is the terminal node for all paths: reached from `sidekick-guide/entry-picker` (just-the-principle / exit) and from `sidekick-guide/guided-tour` (tour done or stopped).
- **No side effects** — per SKILL.md "Boundaries," no Bash, subagents, `data.py`, writes, or scans; selecting `/sidekick-init` or a project is what invokes the next skill, not this node.
