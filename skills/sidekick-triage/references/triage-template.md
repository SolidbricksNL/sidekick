# Triage — {{DATE}}

> Findings from the scheduled scan of connected email, chat, and calendar,
> with a per-project **undistilled-log count** as a heads-up (the check-in
> distills the logs). This is **input for `/sidekick-checkin`** — nothing here
> has been acted on. Suggestions only.

_Run at: {{TIMESTAMP}}_
_Scanned sources: {{SOURCES}}_
_Window: since {{LAST_RUN_OR_WINDOW}}_

---

## Project: {{project-slug}}

_Undistilled logs: {{N}}_  <!-- heads-up only; the check-in distills these -->

### {{source}} — {{short identifier}}
- **Why it matters:** {{one line}}
- **Suggested action:** {{update brain / action / deliverable / reply / agenda / calendar}}
- **Notes:** {{optional, e.g. quoted snippet kept in original language}}

<!-- repeat per finding, grouped under the project it likely belongs to -->

---

## Unassigned / new project?

### {{source}} — {{short identifier}}
- **Why it matters:** {{one line}}
- **Suggested project:** new project? proposed name "{{...}}"
- **Suggested action:** {{...}}

<!-- items that don't match any existing project -->

---

## Summary

- {{N}} findings across {{sources}}.
- {{M}} suggest a possible new project.
- Run `/sidekick-checkin` to review and act on these.
