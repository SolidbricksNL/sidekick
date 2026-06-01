---
name: sidekick-checkin
description: Run the cross-project Sidekick check-in — review triage + agendas and propose gated actions.
---

Invoke the `sidekick-checkin` skill. It will:

1. Walk every non-archived project, cross-referencing the latest `_triage/`
   findings and (if connected) the calendar.
2. Present concrete actions as quick multiple-choice proposals
   (Yes / No / Edit first).
3. Route each approved action through its gatekeeper — brain changes show a diff
   and need approval; output and data-structure changes need confirmation;
   agenda updates are free. Draft replies but never send unprompted. Back up each
   project's `data/` (timestamped) before processing it.
4. Log what was processed in each project's `log/` and leave each touched
   `agenda.md` clean.
