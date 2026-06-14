---
kind: curated
status: current
---

## Graph traversal

The brain is a directed graph of feature-flow nodes under
`flow/<flowId>/<nodeId>.md`. Each node carries `edges:` to
adjacent nodes and `parent:` to its containing parentflow.
Use `flow/_index.json` for byte-deterministic lookups.

## Node reading protocol

When you open a flow node:

1. Read only the `## TLDR (agent)` section first.
2. If your task is answered, stop reading the file.
3. If you need context, edge cases, or implementation detail,
   descend into `## Functional (user facing)` or `## Technical`
   as relevant.
4. Never read `<slug>.notes.md` unless explicitly asked — it is
   curated human content.
5. Never read `<slug>.user.<lang>.md` unless explicitly asked —
   these are auto-derived translations of the source `## Functional
   (user facing)` section. Read the source instead; the side-cars
   exist for the viewer's secondary-language rendering, not for
   agent reasoning.

## Glossary lookup protocol

When you encounter a domain term that could be ambiguous or has
business-specific meaning:

1. Check `meta/glossary/_index.json` for the term (search canonical
   + synonyms).
2. If found, read `meta/glossary/<slug>.md` for the definition.
3. If not found and the term seems important, note it for the user
   — do not guess the meaning.

Flow nodes list relevant glossary entries in their `terms:`
frontmatter — use those as a starting hint when reading a node.

> Note: the glossary is **currently empty** — the Pass 1.5 mechanical
> extractor surfaced only infrastructure identifiers (no domain terms),
> so `meta/glossary/` holds no entries yet. Sidekick's ubiquitous
> language (project, brain, log, output, write disciplines, triage,
> check-in, recipe, dashboard, surface gate) lives in the prose of
> `docs/ARCHITECTURE.md`. Seed glossary terms later if useful.
