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
- **Output sync:** {{OUTPUT_SYNC}}    <!-- No / Yes — mirror each project's output/ to the connected storage as sidekick-<slug>/. Always No when Storage is No. -->
- **Calendar:** {{CALENDAR}}      <!-- No / Google Calendar / Outlook Calendar / Other: ... -->

<!-- Output sync mirrors output/ one-way to external storage (local stays the
     source of truth), additive (never deletes there), on each confirmed output
     write plus a reconcile at the check-in. Only runs when a storage connector
     is actually enabled in Cowork. -->

## Output sync

{{OUTPUT_SYNC_NOTE}}

<!-- When Output sync is Yes: each project's output/ is mirrored to the
     connected storage's root as sidekick-<slug>/. One-way (local canonical),
     additive (external copies are never deleted), updated on each confirmed
     output write and reconciled at /sidekick-checkin. When No, omit or set to
     "Output is kept only in the workspace." -->

## Triage

The `sidekick-triage` skill is intended to run as a **scheduled task in
Cowork**. Set the frequency there (e.g. daily, twice a week). It scans
the connected sources above and writes findings to
`_triage/YYYYMMDD-triage.md`. Run `/sidekick-checkin` to act on them.
