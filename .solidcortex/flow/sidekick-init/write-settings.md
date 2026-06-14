---
flowId: sidekick-init
nodeId: write-settings
type: process
slug: write-settings
status: current
kind: derived
summary: Writes sidekick.settings.md to the Cowork root from the questionnaire answers using the settings template, recording role, languages, and connection intent.
systems: [skills]
domains: [onboarding, write-disciplines]
parent: main/sidekick-init
mainCodeFile: skills/sidekick-init/references/settings-template.md
edges:
  - to: sidekick-init/write-workspace-claude
    via: starts
    label: then write anchor
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Persist the confirmed questionnaire answers to `sidekick.settings.md` in the Cowork root using the settings template.
**Inputs:** confirmed answers (role, chat/output languages, email/messages/storage/calendar, output-sync Yes/No + base path); the template `references/settings-template.md`.
**Outputs:** `sidekick.settings.md` written to the Cowork root with every template field filled from real answers.
**Code anchor:** [skills/sidekick-init/references/settings-template.md](../../../skills/sidekick-init/references/settings-template.md)
**Edges:** → sidekick-init/write-workspace-claude (then write anchor)
**Key rules:**
- Fill every template field from the user's answers; never invent values — use the user's free text for "Other".
- This is the one settings file in the root; the always-on `sidekick` skill reads it at the start of every session.
- Recording a connection here does not enable it — enabling happens in Cowork's connector settings.

## Functional (user facing)

### Why use this?
This step turns your answers into the single profile Sidekick reads at the start of every session — your role, your languages, and which tools you want in scope. From here on, Sidekick chats in your language, writes deliverables in your chosen output language, and acts in the role you described.

### What it does
- Saves one settings file to the top of your workspace.
- Records your role and your chat and default output languages.
- Records your connection choices for email, messages, storage, and calendar exactly as you gave them — including "Other" answers in your own words.
- Records whether two-way output sync is on and, if so, the storage folder it should mirror to.

### Behind the scenes
The file is plain, human-readable text you can re-read any time. Nothing here is computed or guessed: each line comes straight from an answer you confirmed. Re-running setup overwrites this file with your new answers.

### Pro tips
- To change anything later, re-run `/sidekick-init` — that re-asks the questions and rewrites this file.
- The settings file is yours to read; it documents what Sidekick believes about your setup at a glance.

### Related
- [sidekick-init/run-questionnaire](run-questionnaire.md) — collects the answers written here.
- [sidekick-init/write-workspace-claude](write-workspace-claude.md) — the next step, which writes the always-on workspace rules.

## Technical

**Main code locations**
- `skills/sidekick-init/references/settings-template.md` — the canonical structure: `## Role`, `## Languages` (Chat / Default output), `## Connections` (Email / Messages / Storage / Output sync / Output sync base path / Calendar), `## Triage`. Placeholders (`{{ROLE}}`, `{{CHAT_LANGUAGE}}`, etc.) are filled from the answers.
- `skills/sidekick-init/SKILL.md` — "Writing `sidekick.settings.md` and the workspace `CLAUDE.md`" section drives this write as file 1 of 2 on confirmation.

**Output file.** `sidekick.settings.md` at the Cowork root. It is the settings layer described in ARCHITECTURE §8 and the discriminator the surface gate keys on (its presence marks an active workspace). The always-on `sidekick-core` skill reads it every session for role and language adaptation (§9).

**Field mapping.** Email = Yes/No; Messages = No/Slack/Teams/Google Chat/Other; Storage = No/Outlook(OneDrive)/Google Drive/Other; Output sync = Yes/No (per-project folders derived at runtime, never written here); Output sync base path = blank or a mounted/synced folder path; Calendar = No/Google/Outlook/Other. "Other" carries the user's literal text. Init records intent only — no connector is toggled.

**Write discipline.** Single deterministic write of one root file; no diff/approval loop is required for the settings file itself because the user already confirmed all answers in the questionnaire. On a re-configure run this overwrites the prior settings (the user opted into overwrite at the gate).

**Dependencies.** Upstream: `sidekick-init/run-questionnaire` (confirmed answers). Downstream: `sidekick-init/write-workspace-claude`, written immediately after as the second of the two root files.
