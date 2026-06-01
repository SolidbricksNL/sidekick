---
name: sidekick-init
description: Set up or reconfigure the Sidekick workspace (role, languages, connections) and scaffold the first project.
---

Invoke the `sidekick-init` skill. It will:

1. Ask a short multiple-choice questionnaire — role, chat language, default
   output language, and email/messages/storage/calendar connections.
2. After a summary and confirmation, write `sidekick.settings.md` to the Cowork
   root, scaffold the first project, and create the `_triage/` and
   `_archive/projects/` folders.
3. Explain how to schedule triage and which connectors to enable.

It records intent only — it never turns a connector on.
