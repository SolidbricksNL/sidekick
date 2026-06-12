# Sidekick — guide content (single source of truth)

This file is the **only** content source for the `sidekick-guide` tour. The
SKILL.md orchestrates; it renders what is written here and invents nothing.
Adding a new skill to the plugin = adding one entry to the `register` block
below. `scripts/validate-structure.mjs` (Check 8) fails CI if any skill
folder has no entry here, so the guide can never silently fall behind.

Content below is written in **English as the canonical form**. Render it in
the user's chat language (from `sidekick.settings.md`); only the surface
text adapts, never the meaning. Do not expand, embellish, or "improve" a
blurb at render time.

---

## Core principle (the tour opener)

Sidekick fixes the two ways Cowork work gets lost: everything dumped into
the chat (gone at the next compaction) and scattered, unstructured working
documents. It does that with **two ideas**:

**1. Everything lives in a project.** Each piece of work is a folder under
`projects/<slug>/` with a fixed shape — `log/`, `brain/`, `output/`,
`data/`, an `agenda.md`. Nothing floats loose in the chat or the workspace
root. A strand of work *inside* a project is an **area**, not a new
project.

**2. Three write disciplines decide where things go and who approves.**

| What | Where | Gatekeeper |
|---|---|---|
| Process, work-in-progress, thinking out loud | `log/` | Written **freely** |
| Durable, distilled knowledge | `brain/` | **Diff + your approval** |
| Deliverables (Word, Excel, PDF, …) | `output/` | **Confirm** create/edit/delete |
| Structured data — a new table or column | `data/` | **Confirm** (plain language) |

The logbook is free so the chat stays clean (log to disk, summarize in
chat). The brain and output are gated because they're durable — you stay
the gatekeeper. Structured data lives in plain JSON tables reached only
through the bundled `data.py` helper; adding rows that fit is free, only
*structure* changes are confirmed.

Every skill below is built on top of these two ideas. The always-on
`sidekick-core` skill *is* this principle in action; the others are tools
that operate on the same project structure.

---

## Tour order (groups)

The guided tour walks the groups in this order. Each group is one step with
a check-in after it.

1. `basis` — **De basis (altijd aan)**: the engine and the principle.
2. `setup` — **Aan de slag**: first-time setup.
3. `present` — **Je werk presenteren**: turn data into reports & dashboards.
4. `overview` — **Overzicht houden**: read-only glances across projects.
5. `stay-on-top` — **Niets missen**: scan inputs, then act on them.
6. `housekeeping` — **Afronden / opruimen**: retire finished projects.
7. `guide` — **Deze gids**: this skill itself.

---

## Register

```yaml
skills:
  - slug: sidekick-core
    group: basis
    title: "The always-on backbone"
    command: "automatic — always on, no command"
    blurb: "The engine behind everything. It works out which project you're
      in, keeps the chat clean by logging process to disk, and enforces the
      three write disciplines (free log, gated brain, confirmed output and
      data). You never call it — it fires whenever you do real work."
    when: "Always. It activates the moment you start substantive work; the
      principle of the whole plugin lives here."
    triggers:
      - "starting work or saying 'let's work on X'"
      - "sharing a document or asking for analysis"
      - "asking a question about a project's records"

  - slug: sidekick-init
    group: setup
    title: "Set up your workspace"
    command: "/sidekick-init"
    blurb: "One-time (or re-run) setup. A short multiple-choice
      questionnaire — your role, chat language, default output language, and
      which email/chat/storage/calendar to connect — then it writes
      sidekick.settings.md, scaffolds your first project, and explains how to
      schedule triage."
    when: "The first thing to run on a fresh workspace, or whenever you want
      to change your role, languages, or connections."
    triggers:
      - "/sidekick-init"
      - "set up / configure my Sidekick"
      - "the workspace isn't initialized yet"

  - slug: sidekick-report
    group: present
    title: "Reports & dashboards over your data"
    command: "/sidekick-report"
    blurb: "Turns a project's structured data/ store into things a human can
      read and re-run: saved report recipes and interactive tabbed HTML
      dashboards. It reads data only through data.py — never a raw file — so
      the numbers always match the store."
    when: "When you want to see, chart, present, or re-run a view over stored
      table data."
    triggers:
      - "/sidekick-report"
      - "make a dashboard / chart revenue by line"
      - "give me the monthly breakdown again"

  - slug: sidekick-status
    group: overview
    title: "Where does everything stand?"
    command: "/sidekick-status"
    blurb: "A fast, read-only glance across every project: open agenda items,
      how many logs still need distilling, the last check-in date, your data
      tables with row counts, and what's gone quiet. It changes nothing and
      proposes nothing — a dashboard, not a decision point."
    when: "When you want a quick overview without making any decisions."
    triggers:
      - "/sidekick-status"
      - "status / give me an overview"
      - "what's going on across my projects"

  - slug: sidekick-find
    group: overview
    title: "Recall across projects"
    command: "/sidekick-find"
    blurb: "Cross-project recall. It searches every project's brain, logs,
      agendas, and data tables and reports the hits as project -> file ->
      snippet. Read-only: it finds and reports, and offers to open a match,
      but never writes."
    when: "When you know something was decided or mentioned but not where."
    triggers:
      - "/sidekick-find"
      - "where did we decide X"
      - "which project mentions Y / what do we know about Z"

  - slug: sidekick-triage
    group: stay-on-top
    title: "Scan your inputs (scheduled)"
    command: "/sidekick-triage"
    blurb: "A read-only scan of your connected email, chat, and calendar,
      bundled into one timestamped findings file in _triage/. Built to run
      unattended as a scheduled Cowork task — it never writes to a project
      brain or log and never acts on your behalf."
    when: "Runs on a schedule (or on demand) to gather what needs attention.
      Its output is the raw material for the check-in."
    triggers:
      - "/sidekick-triage"
      - "attached as a scheduled task"
      - "scan my inbox / messages"

  - slug: sidekick-checkin
    group: stay-on-top
    title: "Review and act"
    command: "/sidekick-checkin"
    blurb: "Your cross-project review. It reads each project's agenda,
      cross-references the latest triage findings and the calendar, and
      proposes concrete actions per project — one at a time through the
      picker. This is where triage suggestions become real actions, but only
      with your go-ahead, item by item."
    when: "When you want to act on what triage and your agendas surfaced —
      the decision moment paired with status/triage."
    triggers:
      - "/sidekick-checkin"
      - "check-in / what needs my attention"
      - "go through the triage findings"

  - slug: sidekick-archive
    group: housekeeping
    title: "Retire a project"
    command: "/sidekick-archive"
    blurb: "Retire a finished or dormant project by moving its whole folder
      to _archive/. Nothing is ever deleted, so it's fully reversible.
      Archived projects drop out of detection, triage, and check-in but stay
      consultable."
    when: "When a project is done or has gone quiet and you want it out of
      the active set."
    triggers:
      - "/sidekick-archive"
      - "archive / close out / shelve a project"
      - "retire this project"

  - slug: sidekick-guide
    group: guide
    title: "This guide"
    command: "/sidekick-guide"
    blurb: "This skill. An interactive tour of the plugin — the core
      principle, plus what each skill does and when to reach for it — with a
      check-in after each step so you can go deeper or ask a question. Pure
      conversation; it reads nothing but your settings and changes nothing."
    when: "When you're new, onboarding a colleague, or unsure which skill
      fits the job at hand."
    triggers:
      - "/sidekick-guide"
      - "how does sidekick work / explain the plugin"
      - "what can you do / I'm new"
```
