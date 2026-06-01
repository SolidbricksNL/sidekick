---
name: sidekick-find
description: Read-only cross-project recall — search all projects' brain, logs, agendas, and data for a topic.
---

Invoke the `sidekick-find` skill with the user's query. It will:

1. Search every non-archived project's `brain/`, `log/`, and `agenda.md` for
   the query (read-only — it writes nothing).
2. For structured data, use `data.py info`/`query` to spot tables, columns, or
   values that match.
3. Return a short prose list of hits: project → file → snippet, in the original
   language.
4. If you then want to act on a hit, offer — via the interactive picker — to
   open that project and hand off to the normal flow.
