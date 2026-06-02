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
- **Output sync:** {{OUTPUT_SYNC}}    <!-- No / Yes. Always No when Storage is No. -->
- **Calendar:** {{CALENDAR}}      <!-- No / Google Calendar / Outlook Calendar / Other: ... -->

<!-- Output sync records ONLY Yes or No here — nothing per project. When Yes,
     Sidekick syncs each project's output/ with the connected storage under a
     folder named with the fixed prefix "sidekick" plus the project slug
     (sidekick-<slug>). That per-project postfix is derived at runtime and is
     NEVER written into this file. Only runs when a storage connector is
     actually enabled in Cowork. -->

## Triage

The `sidekick-triage` skill is intended to run as a **scheduled task in
Cowork**. Set the frequency there (e.g. daily, twice a week). It scans
the connected sources above and writes findings to
`_triage/YYYYMMDD-triage.md`. Run `/sidekick-checkin` to act on them.
