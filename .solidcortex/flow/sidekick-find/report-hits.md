---
flowId: sidekick-find
nodeId: report-hits
type: process
slug: report-hits
status: current
kind: derived
summary: Rank and group markdown and data hits into a short prose list (project to file to one-line snippet) with snippets in their original language, leading with the most relevant or stating plainly when nothing matched.
systems: [skills]
domains: [project-model]
parent: main/sidekick-find
mainCodeFile: skills/sidekick-find/SKILL.md
edges:
  - to: sidekick-find/open-project-picker
    via: starts
    label: offer to open a hit
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Merge, rank, and present the recall results as a short prose list of hits grouped by project.
**Inputs:** Markdown hits from search-markdown; structured-data hits from probe-data-tables; the chat language from settings.
**Outputs:** A grouped, ranked hit list (project → file → one-line snippet) shown to the user, or a plain "nothing matched"; offers to open a hit.
**Code anchor:** [skills/sidekick-find/SKILL.md](../../../skills/sidekick-find/SKILL.md)
**Edges:** ← sidekick-find/search-markdown (feeds), ← sidekick-find/probe-data-tables (feeds), → sidekick-find/open-project-picker (starts)
**Key rules:**
- Snippets stay in their original language; only the framing is in the chat language.
- Lead with the most relevant hit; group by project.
- When nothing matches, say so plainly and suggest a broader term — never invent hits.

## Functional (user facing)

### Why use this?
After the search has swept notes and data across every project, you want one clean answer, not two raw piles of matches. This step turns everything found into a short, ranked list you can read at a glance — so "where did we decide X?" comes back as a handful of pointers, most-relevant first.

### What it does
- Pulls together both kinds of findings — matches from your notes and matches from your data — into one list.
- Groups the results by project so related hits sit together.
- Shows each hit as project → file → a one-line snippet, leading with whatever looks most relevant.
- Keeps each snippet in the language it was written in, while talking to you in your chat language.

### When nothing matches
If the search comes up empty, this step says so plainly and suggests a broader or different term to try. It will not pad the answer with hits that aren't really there — an honest "nothing found" is the correct result.

### Behind the scenes
This is where the two parallel searches converge. The ranking weighs how well each match fits your question and trims each hit to just enough context to be useful, rather than dumping whole files. Once the list is shown, and only if you want to act on a result, it hands off to the step that can open the matching project for you.

### Pro tips
- Read top-down: the list is ordered, so the first hit is the one most likely to answer you.
- A "nothing found" with a suggested broader term is a cue to loosen your wording, not a dead end.

### Related
- sidekick-find/search-markdown — supplies the prose-note hits this step ranks.
- sidekick-find/probe-data-tables — supplies the structured-data hits this step ranks.
- sidekick-find/open-project-picker — the optional follow-up to open a chosen hit.

## Technical

**Main code.** `skills/sidekick-find/SKILL.md`, the "Output" section. The skill is a prose-instruction file; this node is the agent assembling the final response from the two upstream search nodes.

**Merge & rank.** Inputs are the markdown hits from `sidekick-find/search-markdown` and the structured-data hits (matching tables/columns/values + rows) from `sidekick-find/probe-data-tables`. Output is a short prose list grouped by project, each entry rendered as *project → file → one-line snippet*, ordered most-relevant-first. No whole-brain summaries — only the matching lines with minimal context.

**Language handling.** Snippets are emitted in their original language (preserving the user's source languages); the surrounding framing uses the chat language read from `sidekick.settings.md` at intake. This is the convergence point where the language rule, applied loosely upstream, is enforced in the rendered output.

**Empty result.** When neither upstream node produced a match, the node states this plainly and suggests a broader term. It must not fabricate hits — an explicit no-match is the contract.

**Hand-off.** After presenting results, it offers — only if the user wants to act on a hit — to open that project via `sidekick-find/open-project-picker`. Opening a project is the sole follow-up; everything else remains read-only. Per `docs/ARCHITECTURE.md` §11b the entire skill writes nothing, so no backup or gatekeeper is involved.

**Dependencies.** Consumes `sidekick-find/search-markdown` and `sidekick-find/probe-data-tables`; emits to `sidekick-find/open-project-picker`. Parented to `sidekick-find/recall-query-intake`.
