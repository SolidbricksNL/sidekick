---
flowId: sidekick-find
nodeId: search-markdown
type: process
slug: search-markdown
status: current
kind: derived
summary: Text-search every non-archived project's brain/, log/, and agenda.md for the query terms and obvious variants, treating subproject/area subfolders as part of the parent project.
systems: [skills]
domains: [project-model, write-disciplines]
parent: main/sidekick-find
mainCodeFile: skills/sidekick-find/SKILL.md
edges:
  - to: sidekick-find/report-hits
    via: starts
    label: feed markdown hits
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Text-recall half of the search — greps each non-archived project's prose (brain, logs, agenda) for the query and obvious variants.
**Inputs:** Validated query from recall-query-intake; the shortlist of non-archived projects; each project's `brain/`, `log/`, and `agenda.md` markdown.
**Outputs:** Markdown hits (project → file → matching lines with context) fed to report-hits.
**Code anchor:** [skills/sidekick-find/SKILL.md](../../../skills/sidekick-find/SKILL.md)
**Edges:** ← sidekick-find/recall-query-intake (parent), → sidekick-find/report-hits (starts)
**Key rules:**
- Match on file content, not just filenames — markdown is grep-able.
- Report an area subfolder's hit under its parent project (note the area), never as a separate project.
- Read-only: search and quote, never write, distill, or edit.

## Functional (user facing)

### Why use this?
Most of what a project "knows" lives in plain notes — the distilled brain, the running logs, and the agenda. This step reads all of those across every active project at once, so a decision or fact you wrote down weeks ago in one project surfaces even when you've half-forgotten where it was.

### What it does
- Scans three places per project: the distilled brain, the working logs, and the agenda.
- Matches on the actual words inside the files, not just file names, so a buried mention still counts.
- Tries obvious variants and synonyms of your terms, not only an exact spelling.
- Keeps just enough surrounding text on each hit to make the snippet useful, without dumping whole files.

### How areas are handled
If a project has areas (sub-folders for distinct strands of work), their notes are searched too — but any match is reported under the parent project, with the area noted, rather than appearing as if it were a separate project. This keeps results grouped the way you actually organised the work.

### Behind the scenes
This text sweep runs alongside the structured-data probe; the two never block each other. Whatever this step finds is handed to the ranking step, which interleaves it with any data matches and orders everything by relevance.

### Pro tips
- The more distinctive your term, the cleaner the result — a unique name or phrase beats a common word.
- If you suspect a fact lives in a log you never distilled, it's still found here: logs are searched directly, distilled or not.

### Related
- sidekick-find/recall-query-intake — supplies the query and project list this step searches.
- sidekick-find/probe-data-tables — the parallel search over structured data.
- sidekick-find/report-hits — ranks and presents what this step finds.

## Technical

**Main code.** `skills/sidekick-find/SKILL.md`, step 2 of "How to search" ("Text search"). The skill is a prose-instruction file; the actual searching is the agent applying grep-style matching to the listed markdown.

**Scope.** Per non-archived project (from the parent intake node), three targets: `brain/` (distilled knowledge), `log/` (working/undistilled notes), and `agenda.md`. Subproject/area subfolders (`brain/<area>/`, `output/<area>/`) are searched as part of the parent — a hit there is attributed to the parent project with the area noted, per the `project-structure.md` canonical layout and the `write-disciplines` routing rules.

**Matching.** Content-level match (not filename-only), including obvious variants/synonyms of the query terms. Hits are returned as project → file → matching line(s) with minimal surrounding context — never whole-file summaries.

**Boundaries.** Strictly read-only: no writes, no distillation, no edits or deletes anywhere in `brain/`, `log/`, or `agenda.md`. Snippets are preserved in their original language; only the framing is in the chat language (handled downstream in report-hits).

**Dependencies.** Consumes the query + project list from `sidekick-find/recall-query-intake`. Emits to `sidekick-find/report-hits`, which merges these markdown hits with the structured-data hits from `sidekick-find/probe-data-tables`. No Python or MCP involvement in this node — it is pure markdown recall.
