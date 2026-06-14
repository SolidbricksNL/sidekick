---
flowId: sidekick-init
nodeId: run-questionnaire
type: process
slug: run-questionnaire
status: current
kind: derived
summary: Multiple-choice setup questionnaire that collects role, chat and output languages, email/messages/storage/calendar connections, and optional output-sync base path, then summarizes for confirmation.
systems: [skills]
domains: [onboarding]
parent: main/sidekick-init
mainCodeFile: skills/sidekick-init/SKILL.md
entry: true
edges:
  - to: sidekick-init/write-settings
    via: starts
    label: confirmed → persist
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Walk the user through the setup questionnaire (role, languages, connections, optional output-sync path) and summarize the answers for confirmation.
**Inputs:** user answers to 7 questions, asked one at a time as multiple choice; free text accepted for role and "Other".
**Outputs:** a captured answer set (role, chat language, output language, email/messages/storage/calendar, output-sync Yes/No + base path) plus an explicit user confirmation gate.
**Code anchor:** [skills/sidekick-init/SKILL.md](../../../skills/sidekick-init/SKILL.md)
**Edges:** → sidekick-init/write-settings (confirmed → persist)
**Key rules:**
- One question at a time, multiple choice (2–4 options + an escape hatch); open text only for role / project name / "Other".
- Init records intent only — answering "Yes" to a connector never turns it on.
- Output-sync base path must be a mounted/synced Drive or OneDrive folder; blank ⇒ sync stays idle.
- Summarize every answer and get explicit confirmation before anything is written.

## Functional (user facing)

### Why use this?
This is the short interview that personalizes Sidekick to you: who you are, what languages to use, and which of your tools (email, chat, storage, calendar) it may eventually draw on. Answering takes a minute because every question is a quick tap.

### How to use it
1. Answer each question as it appears — most are a pick from 2–4 options, with a free-text escape for anything that doesn't fit.
2. State your **role** (e.g. "Managing Director of a software company"). This shapes the kind of advice Sidekick gives.
3. Choose a **chat language** (how Sidekick talks to you) and a **default output language** (the language of documents and sheets). These can differ — chat in Dutch, deliverables in English, for instance.
4. Say which connections you want Sidekick to consider later: **email**, a **messaging platform**, **storage**, and a **calendar**.
5. If you connect storage, decide whether to keep your finished deliverables **in step with an external folder, both ways**. If yes, point Sidekick at a folder that already syncs to your storage on this machine.
6. Review the summary of all your answers and confirm. Nothing is saved until you do.

### What it does
- Collects your role, chat language, and default output language.
- Records, per channel, whether you want email / messages / storage / calendar in scope — and which provider where it matters.
- Offers two-way output sync only as a follow-up to connecting storage, and captures a base folder for it.
- Produces a single recap and waits for your go-ahead.

### Connections are intent, not switches
Saying "Yes" to email, chat, storage, or calendar here only records that you want it. Each connector is still turned on by you, later, in Cowork's connector settings.

### About output sync
Output sync keeps each project's finished deliverables and an external storage folder matched in both directions, so files appear in (say) Google Drive and edits made there flow back. If the same file changes in both places at once, Sidekick asks which version to keep, and it never deletes a file just because of syncing. The folder you give must be one your Drive or OneDrive desktop app already syncs; without such a folder, sync simply stays idle until you set one.

### Pro tips
- Pick "Other (specify)" whenever your provider or language isn't in the list — free text is accepted.
- Chat and output language are independent; set them to match your real habits.
- If you want output sync but don't yet have a synced folder, you can leave the path blank and add it later.

### Related
- [sidekick-init/surface-gate-check](surface-gate-check.md) — the gate that runs before these questions.
- [sidekick-init/write-settings](write-settings.md) — persists these answers once you confirm.

## Technical

**Main code locations**
- `skills/sidekick-init/SKILL.md` — "The questionnaire" section enumerates the seven questions (role, chat language, default output language, email, messages, storage + 6b output sync + base path, calendar), the multiple-choice interaction rule, and the summarize-then-confirm gate.
- `skills/sidekick-init/references/settings-template.md` — the field shapes these answers map onto (Yes/No, provider enums, base-path string).

**Question set.** Q1 role (free text), Q2 chat language, Q3 default output language, Q4 email (Yes/No), Q5 messages (No/Slack/Teams/Google Chat/Other), Q6 storage (No/Outlook OneDrive/Google Drive/Other), Q6b output sync (Yes/No) and — when Yes — a base path on a mounted/synced Drive or OneDrive folder, Q7 calendar (No/Google/Outlook/Other). See ARCHITECTURE §8 (settings layer) and §13.

**Interaction contract.** Multiple choice throughout (plugin-wide style; see `../sidekick-core/references/interaction-style.md`), 2–4 options plus an escape hatch, open questions only for role / project name / "Other". Communicate in the user's chat language (already established by the gate node when previously unknown).

**Confirmation boundary.** This node produces no files. The summarize-and-confirm step is the hand-off boundary: only on a clear confirmation does control pass to `sidekick-init/write-settings`. Output-sync base path is recorded but not validated against the filesystem here — blank simply means sync does not run (no connector fallback for files; the connector route was dropped because moving a binary through it forced base64-through-the-model).

**Dependencies.** Upstream: `sidekick-init/surface-gate-check`. Downstream: `sidekick-init/write-settings`.
