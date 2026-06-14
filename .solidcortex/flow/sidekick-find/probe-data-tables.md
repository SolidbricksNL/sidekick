---
domains:
  - structured-data
edges:
  - label: feed data hits
    to: sidekick-find/report-hits
    via: starts
flowId: sidekick-find
generatedAt: 2026-06-14T11:55:56Z
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generator: solidcortex@0.17.0
kind: derived
mainCodeFile: skills/sidekick-find/SKILL.md
nodeId: probe-data-tables
parent: main/sidekick-find
related:
  - structured-data/query-data
  - structured-data/info-discover
  - sidekick-status/read-data-tables
  - sidekick-report/query-data-store
slug: probe-data-tables
status: current
summary: Resolve the data.py helper, run read-only info/query against each project's data/ to spot tables, columns, or values matching the query, and pull relevant rows — never touching raw JSON directly.
systems:
  - skills
  - python-helpers
type: process
---

## TLDR (agent)
**Purpose:** Structured-data half of the search — uses data.py info/query to find tables, columns, or values matching the query and pull the relevant rows.
**Inputs:** Validated query from recall-query-intake; each project's `data/`; the resolved `data.py` helper path.
**Outputs:** Data hits (matching tables/columns/values + relevant rows) fed to report-hits.
**Code anchor:** [skills/sidekick-find/SKILL.md](../../../skills/sidekick-find/SKILL.md)
**Edges:** ← sidekick-find/recall-query-intake (parent), → sidekick-find/report-hits (starts)
**Key rules:**
- Go through `data.py` only — never read or grep the raw `data/*.json` files.
- Read-only commands only: `info` and `query` (SELECT); never insert/update/delete/create/addcol.
- Resolve the helper via `find` because `$CLAUDE_PLUGIN_ROOT` is unset in the shell.

## Functional (user facing)

### Why use this?
Not everything you record is prose — pipelines, deal lists, tallies and tables live as structured data. This step looks inside that data for you, so a recall question like "which deals mention Rabobank?" can be answered from the numbers and rows, not just the notes.

### What it does
- Checks each project that has structured data for tables, columns, or recorded values that match your question.
- When something matches, it pulls back just the relevant rows so you see the actual records, not a vague pointer.
- Reads the data only — it never changes a single value.

### Behind the scenes
The probe first asks each project's data what tables and columns exist and which category values are on file, then matches your query against those. Only when there's a match does it run a read-only lookup to fetch matching rows. It always works through the data helper, never poking at the underlying files directly, which is what keeps the search safe and consistent. This runs at the same time as the text sweep, and its findings join the same ranked result list.

### Pro tips
- Exact category spellings help: the probe can see the distinct values a column actually holds, so the closer your term, the better the match.
- If a project has no structured data, it's simply skipped here and still covered by the text search.

### Related
- sidekick-find/recall-query-intake — supplies the query and project list.
- sidekick-find/search-markdown — the parallel search over prose notes.
- sidekick-find/report-hits — ranks and presents the matching rows alongside text hits.

## Technical

**Main code.** `skills/sidekick-find/SKILL.md`, step 3 of "How to search" ("Structured data"), plus step 4's prohibition. Backed by `skills/sidekick-core/scripts/data.py`, specifically the read-only paths `cmd_info` (`data.py info`) and `query`/`cmd_query` (`data.py query`).

**Helper resolution.** `$CLAUDE_PLUGIN_ROOT` is unset in the shell, so the helper is located at runtime:
`SK="$(find ~ -ipath '*/sidekick-core/scripts' -type d 2>/dev/null | head -1)"`, then commands run as `python3 "$SK/data.py" …`.

**Probe sequence.**
1. For each project with a `data/` directory, run `python3 "$SK/data.py" info --project projects/<slug>`. `cmd_info` enumerates each `*.json` table (skipping `_schema.json`), its columns from `_schema.json` (or inferred), per-table `rowcount`, and — for low-cardinality columns (≤ `_ENUM_MAX`) — the distinct `values` list, giving exact-spelling category matches.
2. If a table/column/value matches the query, run a read-only `query --project … --sql "SELECT …"`. `query()` builds a throwaway in-memory SQLite from the JSON, runs the SELECT, and returns `{rows, rowcount}`; on a bad column/table it appends the real schema (`| available: deals(product, platform, arr)`) so the agent can self-correct.

**Read-only enforcement.** `query()` rejects anything not starting with `select`/`with` (raises `ValueError`). The skill further forbids `insert`/`update`/`delete`/`create`/`addcol` — only `info`/`query`. Raw `data/*.json` files are never read or grepped directly; all access is mediated by `data.py` (consistent with the `structured-data` / `data-discipline` rules).

**Dependencies.** Consumes the query + project list from `sidekick-find/recall-query-intake`; emits matching tables/values/rows to `sidekick-find/report-hits`, which merges them with markdown hits from `sidekick-find/search-markdown`. Depends on `skills/sidekick-core/scripts/data.py` and the per-project `data/` layout.
