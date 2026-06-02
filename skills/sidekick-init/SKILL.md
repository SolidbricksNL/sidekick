---
name: sidekick-init
description: One-time (or re-run) setup for Sidekick. Use when the user runs /sidekick-init, when sidekick.settings.md is missing, or when the user asks to set up, configure, or re-configure their Sidekick workspace, role, languages, or connections. Walks the user through a short multiple-choice questionnaire (role, chat language, default output language, email/messages/storage/calendar connections, and — when storage is connected — optional output sync to that storage), writes sidekick.settings.md to the Cowork root, scaffolds at least one initial project, and then explains how to schedule the triage and which connectors may need enabling.
---

# Sidekick — Init

You set up the Sidekick workspace. Be friendly, brief, and
non-technical. Ask the questions one at a time as multiple choice so the
user can answer fast. Confirm before writing files.

**Ask with multiple choice throughout** (2–4 short options, plus an
escape hatch). This is the plugin-wide interaction style — see
`../sidekick-core/references/interaction-style.md`. Use open questions only for
free-form answers like the role or a project name.

## Before you start

- Check whether `sidekick.settings.md` already exists in the Cowork root.
  - If it exists, tell the user their workspace is already set up, show a
    short summary of the current settings, and ask whether they want to
    **re-configure** (re-run the questionnaire and overwrite) or **keep**
    the current settings. Only proceed on a clear answer.
- Communicate in the user's language. If you don't yet know it (no
  settings), ask the chat-language question first and switch to that
  language for the rest of the setup.

## The questionnaire

Ask these one at a time. Offer the options as a short multiple-choice
list. Accept a free-text answer where it makes sense (role, "other").

1. **Role.** "What is your role? This lets me act as a personal advisor
   tuned to your work." Free text (e.g. "Managing Director of a software
   company", "client consultant", "marketer"). Offer a few examples but
   accept anything.

2. **Chat language.** "Which language should I use when talking with you
   here in the chat?"
   - Options: English / Nederlands / Deutsch / Français / Other (specify).

3. **Default output language.** "Which language should I use by default
   for deliverables — documents, sheets, slides — unless you ask for
   another language for a specific one?"
   - Options: English / Nederlands / Deutsch / Français / Other (specify).
   - Note to the user: this can differ from the chat language (e.g. chat
     in Dutch, documents in English).

4. **Email connection.** "Do you want to connect email, so the triage
   can scan recent messages?"
   - Options: Yes / No.

5. **Messages / chat connection.** "Do you want to connect a messaging
   platform for the triage to scan?"
   - Options: No / Slack / Microsoft Teams / Google Chat / Other (specify).

6. **Storage connection.** "Do you want to connect a storage location?"
   - Options: No / Outlook (OneDrive) / Google Drive / Other (specify).

   **6b. Output sync.** "Shall I keep your finished deliverables in step with
   an external storage folder, both ways — so they show up in e.g. Google
   Drive, and edits made there come back into your workspace?"
   - Options: Yes / No. Record in **Output sync** (Yes/No only).
   - Keep it non-technical: this keeps `output/` and the storage folder in step
     **both directions**; if the same file is changed in both places at once,
     Sidekick asks which version to keep, and it never deletes a file as a side
     effect of syncing.
   - **If Yes, ask for the base path:** "Give me the folder that already syncs
     to your storage on this machine — a Google Drive for Desktop or OneDrive
     folder, e.g. `G:\My Drive\sidekick`. I'll copy each project's deliverables
     into `<that folder>\<project>\output\`." Record it in **Output sync base
     path**. Explain plainly: it must be a folder the Drive/OneDrive desktop
     app syncs (so files copied there actually upload); without such a path,
     sync can't run. Sidekick moves files by **copying** them (works for Excel,
     PowerPoint, PDF) — it never routes a file through the chat.
   - If they don't have such a folder, record Output sync **Yes** but leave the
     base path blank, and note sync stays idle until they set one (or set it No).

7. **Calendar connection.** "Do you want to connect a calendar, so the
   triage and check-in can take your agenda into account?"
   - Options: No / Google Calendar / Outlook Calendar / Other (specify).

After the questions, **summarize all answers** and ask for confirmation
before writing anything.

## Writing `sidekick.settings.md`

On confirmation, write `sidekick.settings.md` to the Cowork root using
the structure in `references/settings-template.md`. Fill in every field
from the answers. Do not invent values; for "Other" use the user's
specified text.

**Important:** init does **not** turn any connector on. It only records
what the user wants. Actually enabling a connector (email, chat, storage,
calendar) is something the user does themselves in Cowork's connector
settings.

## Scaffolding the first project

Setup must roll out the structure, so create **at least one** project:

1. Ask: "What's the first project you want to work in? Give it a short
   name." Derive a `kebab-case` slug from the answer.
2. Scaffold `projects/<slug>/` exactly as the main `sidekick` skill does:
   - `CLAUDE.md` from `../sidekick-core/references/project-claude-template.md`,
     with the project name filled in.
   - `agenda.md` from `../sidekick-core/references/agenda-template.md`.
   - empty `brain/`, `log/`, `archive/`, `output/` directories.
   - do **not** create `data/` yet (lazy — appears on the first table).
3. Also create the root-level system folders if absent: `_triage/` and
   `_archive/projects/`.

Create only a **single top-level** project (a direct child of `projects/`).
Do **not** create nested subprojects or areas during init, and never a
`projects/<parent>/<sub>/` folder — a project is always `projects/<slug>/`.
Subprojects/areas (a strand within a project) are introduced later by the
main `sidekick` skill as `brain/<sub>/` + `output/<sub>/` subfolders, never as
nested projects (see `../sidekick-core/references/project-structure.md`).

## Closing: explain scheduling and connectors

After everything is written, give the user a short, non-technical
wrap-up:

1. **What was created** — settings file, the first project, and the
   system folders.
2. **How to schedule the triage.** Explain that the `sidekick-triage`
   skill is meant to run as a **scheduled task in Cowork**, and that they
   set the frequency themselves there (e.g. daily or twice a week). Point
   them to Cowork's scheduled-tasks feature to set it up. The plugin does
   not set the frequency.
3. **Which connections to enable.** Based on their answers, list the
   connectors they said yes to (email / messages / storage / calendar)
   and remind them that these must be **enabled in Cowork's connector
   settings** for the triage to actually read them. If they chose "No"
   everywhere, note that triage will have nothing to scan until a
   connector is added. **If they turned on output sync,** add that it only
   runs once the **storage connector is enabled** in Cowork — until then
   deliverables stay in the workspace and the mirror catches up at the next
   check-in.
4. **What's next.** They can now just start working — the always-on
   `sidekick` skill will pick the right project and keep things
   structured. They can run `/sidekick-checkin` for a cross-project
   review, and `/sidekick-archive` to archive a finished project.

Keep this wrap-up short and concrete.
