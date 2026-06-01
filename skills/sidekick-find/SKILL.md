---
name: sidekick-find
description: Read-only cross-project recall and search for Sidekick. Use when the user runs /sidekick-find or asks a recall question that spans projects — "where did we decide X", "which project mentions Y", "what do we know about Z", "find/search the brain for …". Searches every non-archived project's brain/, log/, and agenda.md, and uses data.py info/query to spot matching tables, columns, or values. Returns a prose list of hits (project → file → snippet) in the original language. Writes nothing; may offer to open a matching project via the interactive picker. Does NOT change any file. The always-on sidekick-core skill routes clear recall questions here even without the explicit command.
---

# Sidekick — Find (cross-project recall)

You answer "where did we…?" across **all** projects at once — the recall the
per-project session-start read can't give. You are **read-only**: you search
and report, you never write.

## When you run

- The user runs `/sidekick-find <query>`, or
- the user asks a recall question that clearly spans projects ("where did we
  decide the BPD pricing?", "which project has the Rabobank mandate?", "what do
  we know about Norvato?"). The always-on skill may hand these to you.

If the query is vague, ask **one** short clarifying question (free text is fine
here — recall terms are open-ended), then search.

## How to search

1. Read `sidekick.settings.md` for the chat language. List `projects/`
   (non-archived only).
2. **Text search** each project's `brain/`, `log/`, and `agenda.md` for the
   query terms (and obvious variants/synonyms). Markdown is grep-able — match
   on content, not just filenames.
3. **Structured data.** For each project with `data/`, run
   `python3 "$CLAUDE_PLUGIN_ROOT/skills/sidekick-core/scripts/data.py" info --project projects/<slug>`
   to see tables, columns, and the listed category values. If the query matches
   a table/column/value, run a read-only `query` to pull the relevant rows.
   (Fallback path if `$CLAUDE_PLUGIN_ROOT` is unset:
   `~/.claude/plugins/sidekick/skills/sidekick-core/scripts/data.py`.)
4. Never read or `grep` the raw `data/*.json` files — go through `data.py`.

## Output

Return a **short prose list of hits**, grouped by project, each as
*project → file → one-line snippet*, with the snippet in its **original
language**. Lead with the most relevant. If nothing matches, say so plainly and
suggest a broader term — don't invent hits.

Then, **only if the user wants to act** on a hit, offer through the interactive
picker to **open that project** (and hand off to the normal `sidekick-core`
flow). Opening a project is the only follow-up; everything else stays read-only.

## Boundaries

- **Read-only.** Never write, distill, edit, or delete anything; never modify
  `data/` (no `insert`/`update`/`delete`/`create`/`addcol` — only `info`/`query`).
- Preserve the user's languages: snippets in their original language, your
  framing in the chat language.
- Don't summarize a project's whole brain — return the **matching** lines, with
  just enough context to be useful.
