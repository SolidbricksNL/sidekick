# Sidekick settings

> Written by `/sidekick-init`. The always-on `sidekick` skill reads this
> at the start of every session. Re-run `/sidekick-init` to change it.

_Last updated: {{DATE}}_

## Role

{{ROLE}}

<!-- Free text. Drives the advisor's tone, focus, and the kind of advice
     Sidekick gives. Example: "Managing Director of a software company". -->

## Languages

- **Chat language:** {{CHAT_LANGUAGE}}
- **Default output language:** {{OUTPUT_LANGUAGE}}

<!-- Chat language = how Sidekick talks to you in chat.
     Default output language = the language of deliverables unless you
     explicitly ask otherwise for a specific one. These can differ. -->

## Connections

> Recording intent only. Enabling a connector happens in Cowork's
> connector settings — Sidekick does not turn anything on.

- **Email:** {{EMAIL}}            <!-- Yes / No -->
- **Messages / chat:** {{MESSAGES}}   <!-- No / Slack / Microsoft Teams / Google Chat / Other: ... -->
- **Storage:** {{STORAGE}}        <!-- No / Outlook (OneDrive) / Google Drive / Other: ... -->
- **Output sync:** {{OUTPUT_SYNC}}    <!-- No / Yes. -->
- **Output sync base path:** {{OUTPUT_SYNC_BASE_PATH}}   <!-- Blank, or a folder path on a mounted/synced Drive/OneDrive (e.g. G:\My Drive\sidekick). Only used when Output sync is Yes. -->
- **Calendar:** {{CALENDAR}}      <!-- No / Google Calendar / Outlook Calendar / Other: ... -->

<!-- Output sync = two-way sync of each project's output/ with external storage,
     done by the bundled CLI scripts/sync.py (plain file copies, no data through
     the model). Under the base path, each project gets <slug>/output/. Records
     ONLY Yes/No + the base path here — no per-project names.

     Output sync base path must be a MOUNTED/SYNCED folder (Google Drive for
     Desktop, OneDrive) reachable from the workspace, so a copied file is picked
     up by the storage client. BLANK => sync does not run (there is no connector
     fallback for files). The connector route was dropped: moving a binary
     through it forced slow base64-through-the-model. -->

## Triage

The `sidekick-triage` skill is intended to run as a **scheduled task in
Cowork**. Set the frequency there (e.g. daily, twice a week). It scans
the connected sources above and writes findings to
`_triage/YYYYMMDD-triage.md`. Run `/sidekick-checkin` to act on them.
