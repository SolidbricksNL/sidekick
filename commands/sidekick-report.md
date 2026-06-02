---
name: sidekick-report
description: Build a reusable report or interactive dashboard over a project's structured data/ store.
---

Invoke the `sidekick-report` skill with what the user wants to see. It will:

1. Determine the project and read its `data/` shape via `data.py info`
   (data is sourced only through `data.py query` — never a raw JSON read).
2. Reuse a saved report from `brain/reports.md` if the user is asking for one
   again, or build a new one.
3. Render the lightest fit: a chat answer, a markdown table, a sheet, or a
   self-contained **tabbed HTML dashboard** in `output/` (snapshot, not live).
4. Save the report as a recipe in `brain/reports.md` (diff + approval) and
   write the artifact to `output/` (confirmation), in the default output
   language. Refresh = re-run the report.
