# Sidekick — internal rollout note

_Internal. The repo is public (`SolidbricksNL/sidekick`)._

## What Sidekick is

A Claude **Cowork** plugin that turns Cowork into a structured work
environment. It adapts to your role (MD, consultant, marketer, …) and acts as
your personal advisor, while keeping your work organized so nothing important is
lost to chat compaction and no scattered documents pile up.

It fixes Cowork's two habits — dumping everything in the chat, and making
unstructured working docs — by anchoring all work in **projects** and enforcing
three **write disciplines**.

## The mental model: three write disciplines

| You're writing… | Goes to… | What happens |
|---|---|---|
| Process / work-in-progress | `log/` | **Free** — written to disk, chat gets a short summary |
| Durable knowledge | `brain/` | **Diff + your approval** before it's saved |
| A deliverable | `output/` | **You confirm** before it's created/edited/deleted |
| Structured-data **structure** (new table/column) | `data/` | **You confirm** (asked in plain language) |

Structured data lives in plain JSON tables under `data/` (one file per table),
managed by a bundled helper. **Records that fit** an existing table flow in
freely; only structure changes are confirmed. The chat is the steering wheel;
the disk is the workbench.

## Install (one-time)

1. In Cowork, **add the plugin** from the private GitHub repo.
2. Run **`/sidekick-init`** — answer a short multiple-choice setup (role,
   languages, connections). It writes your settings and your first project.
3. **Enable the connectors** you want (email / messages / storage / calendar) in
   Cowork's connector settings — the plugin records intent but never turns them
   on.
4. Optionally attach **`sidekick-triage`** to a Cowork scheduled task.

Then just work. `/sidekick-checkin` reviews across projects; `/sidekick-archive`
retires one (moved, never deleted).

## Before relying on it

Run the ~30-minute checklist in [`MANUAL-TESTS.md`](MANUAL-TESTS.md) in a throwaway
Cowork workspace — it's human-judged and covers init through archive, plus a
prompt-injection safety check on triage.

## Feedback

This is an early **0.2.0**. Send issues, rough edges, and ideas to the repo
(`SolidbricksNL/sidekick`).
