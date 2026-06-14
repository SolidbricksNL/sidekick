---
flowId: sidekick-report
nodeId: report-entry
type: process
slug: report-entry
status: current
kind: derived
summary: The /sidekick-report skill activates, checks the surface gate, reads settings, resolves the target project and its data/ store, loads any saved recipes, and picks the lightest render that answers the ask.
systems: [skills, commands]
domains: [reporting]
mainCodeFile: skills/sidekick-report/SKILL.md
entry: true
edges:
  - to: sidekick-report/query-data-store
    via: starts
    label: source the rows
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Entry point of the reporting flow — activates the `sidekick-report` skill, gates the surface, picks the project + data store, and chooses the lightest render for the ask.
**Inputs:** `/sidekick-report [what they want]` (typed), or a "show/present/visualize/chart/summarize/dashboard the data" intent routed in by always-on `sidekick-core`; needs `sidekick.settings.md` + a project `data/` store.
**Outputs:** A resolved project, loaded recipes (`brain/reports.md`), and a render decision (chat answer / markdown table / sheet / dashboard) → hands off to query-data-store.
**Code anchor:** [skills/sidekick-report/SKILL.md](../../../skills/sidekick-report/SKILL.md)
**Edges:** → sidekick-report/query-data-store (starts — source the rows)
**Key rules:**
- Gate: no `sidekick.settings.md` and no Cowork MCP tools → say this isn't a Sidekick workspace and stop.
- A project with no `data/` store has nothing to report on — say so, point at the data discipline.
- Reporting reads and presents only; it never writes data records (insert/update/delete/create/addcol).
- Pick the lightest render that answers the need — don't build a dashboard for a one-number question.

## Functional (user facing)

### Why use this?
This is where a request to *see* your data starts. Once a project keeps a
structured store, the next thing you usually want is to read it back: the same
question answered again without re-explaining it, or the figures laid out so a
person can actually scan them. This step takes "show me the monthly breakdown
again" or "chart revenue by line" and turns it into the right kind of answer.

### What it does
- Recognizes a reporting request — whether you typed `/sidekick-report` or just
  asked to see, present, chart, summarize, or dashboard the stored data. The
  always-on assistant hands clear "present the data" intents here on its own.
- Confirms you are in a real Sidekick workspace; if you are not, it tells you so
  plainly rather than half-working.
- Figures out which project you mean. If that is unclear, it asks rather than
  guessing.
- Looks up reports you have saved before, so "the monthly one again" just re-runs
  what already exists instead of being rebuilt from scratch.
- Chooses the lightest thing that answers you: a number can be a one-line reply;
  a table you want to keep can be a markdown table or a sheet; something to
  explore becomes the project's dashboard.

### When the project has no data
If the project has no structured store yet, there is nothing to report on. It
says so and points you at the data side of Sidekick — you add records first,
then come back to present them.

### Behind the scenes
It reads your settings to know which language to answer and label things in,
identifies the active project, and loads any previously saved report
definitions so recurring questions are cheap to answer. No data is read yet at
this point and nothing is written — it is purely the routing and setup step.

### Pro tips
- Phrase a recurring request the same way ("the monthly revenue breakdown") and
  it will reuse the saved recipe.
- If you just want a single figure, ask for it directly — you will get a chat
  answer, not a file to open.
- Want a separate dashboard rather than additions to the existing one? Say so
  explicitly; by default everything lands in the one project dashboard.

### Related
- [sidekick-report/query-data-store](query-data-store.md) — the next step, where
  the actual rows are sourced.

## Technical

`skills/sidekick-report/SKILL.md` is the orchestration prompt; `commands/sidekick-report.md`
is the thin `/sidekick-report` command that invokes the skill with the user's
ask. The skill body carries the gate, the work protocol, and the boundaries.

Activation paths:
- Typed `/sidekick-report [ask]` via the command file.
- Routed from the always-on `sidekick-core` skill when it classifies an intent as
  "present/visualize the data."

Setup performed here (no data access, no writes):
1. **Gate** — the `> **Gate:**` blockquote and the description tail: absent
   `sidekick.settings.md` AND no Cowork MCP tools ⇒ refuse as non-Sidekick. This
   mirrors the surface gate every typed skill carries (ARCHITECTURE §1b).
2. **Settings + project** — read `sidekick.settings.md` for chat + output
   language; resolve the active project, or ask via the picker when ambiguous.
   The project must have a `data/` store (`data.py info`), else there is nothing
   to report on.
3. **Load recipes** — read `brain/reports.md` if present, so a "do that report
   again" maps to a saved recipe rather than a fresh derivation.
4. **Choose the render** — lightest fit: a chat answer, a markdown table in
   `log/`, a sheet in `output/`, or the project's standard dashboard.

Boundaries enforced from here on: data is sourced **only** through
`data.py query`/`info` (never a raw `data/*.json` read, never `sqlite3` CLI or
ad-hoc `python`); the layer never writes data records — a request to change
records or structure is handed back to the normal `sidekick-core` data flow. Full
protocol: `skills/sidekick-core/references/reporting.md`; architecture context:
`docs/ARCHITECTURE.md` §7b.

Downstream: hands the render decision to `sidekick-report/query-data-store`, which
performs the read.
