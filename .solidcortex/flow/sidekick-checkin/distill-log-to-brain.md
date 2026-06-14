---
flowId: sidekick-checkin
nodeId: distill-log-to-brain
type: process
slug: distill-log-to-brain
status: current
kind: derived
summary: 'On approval, distill an undistilled log''s durable insights into brain/ (diff + approval) and append the "> distilled to brain: <date>" stamp to that log file so it is not re-detected.'
systems: [skills]
domains: [write-disciplines]
parent: main/sidekick-checkin
related:
  - write-disciplines/brain-write
mainCodeFile: skills/sidekick-checkin/SKILL.md
edges:
  - to: sidekick-checkin/reconcile-output-sync
    via: calls
    label: sweep output sync after approvals
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Folds an approved undistilled log's durable insights into the brain and stamps the log so it is never re-detected.
**Inputs:** trigger: user approves a "distill a log" proposal from the per-project walk; reads the unstamped `log/` file; produces a brain diff.
**Outputs:** brain entry written after approval; `> distilled to brain: <today>` footer appended to the source log; then the output-sync sweep.
**Code anchor:** [skills/sidekick-checkin/SKILL.md](../../../skills/sidekick-checkin/SKILL.md)
**Edges:** ← sidekick-checkin/per-project-walk (parent), → sidekick-checkin/reconcile-output-sync (calls)
**Key rules:**
- Distillation is gated: show the brain diff, write only after approval (brain discipline — never write without a diff).
- The stamp is written only after the brain write succeeds; a deferred log is left unstamped so it resurfaces next check-in.
- The original log stays in `log/` — only the footer line is added; the log file is not moved or deleted.
- Only the check-in writes the distilled stamp; the triage never writes outside `_triage/`.

## Functional (user facing)

### Why use this?
Good thinking often lands in a log during a working session and then sits there. This step is the safety net that makes sure those durable insights actually reach the project's brain — with your approval — so the knowledge is captured where the project will use it, instead of being buried in an old log.

### What it does
- Takes a log the per-project walk flagged as never distilled and pulls its lasting insights — decisions, facts, conclusions worth keeping.
- Shows you exactly what would be added to the brain as a diff, and only writes it once you approve.
- After the brain entry is in, marks the log as done by adding a "distilled to brain" line with today's date, so the same log won't be flagged again.
- Leaves the original log untouched apart from that one stamp line — nothing is deleted or moved.

### When you defer
If you decide a log isn't worth distilling right now, it's simply left without the stamp. It will come back as a proposal at the next check-in, so nothing is forced and nothing is lost.

### Behind the scenes
This closes the loop from log to brain without relying on anyone remembering to write insights back during the session. The brain change goes through the same approval-with-a-diff rule as any other brain edit; the stamp is the bookkeeping that stops a single good discussion from being re-proposed every time.

### Pro tips
- The diff is your control point — if the distillation captured too much or the wrong thing, edit it before approving.
- Because the log keeps its full text and only gains a stamp, you can always go back and read the original discussion later.

### Related
- [per-project-walk](per-project-walk.md) — detects the undistilled log and raises the proposal this step acts on.
- [reconcile-output-sync](reconcile-output-sync.md) — the output-sync sweep run after approvals.

## Technical

Implements the "Distilled logs" bullet of the "Acting on approvals" section in `skills/sidekick-checkin/SKILL.md`, together with ARCHITECTURE §5 (brain write-back safety net) and §6 (distilled-to-brain stamp).

- **Detection upstream.** The undistilled log is found in step 4 of `per-project-walk` (a `log/` file lacking the `> distilled to brain:` footer, excluding files modified within the last hour). This node executes only the approved distillation.
- **Brain write.** Durable insights are distilled (key points, not a copy) and presented as a diff; the write happens only after approval and follows the brain discipline (ARCHITECTURE §2, §5) — no new brain files without asking, update existing lines rather than stacking contradictory versions. Any processed source moves to `archive/` per the general brain rule.
- **Stamp.** On a successful brain write the footer line `> distilled to brain: <today>` is appended to the source `log/` file (ARCHITECTURE §6). This is the only writer of that stamp — the triage never writes outside `_triage/`, so the loop `log → brain` cannot double-process. The exact stamp string is the detection key for the next check-in's scan.
- **Defer path.** No approval ⇒ no brain write ⇒ no stamp; the log stays unstamped and re-surfaces at the next check-in.

**Dependencies.** Parent `sidekick-checkin/per-project-walk` supplies the flagged log and the approval. Calls `sidekick-checkin/reconcile-output-sync` to sweep output sync after the approvals are carried out. No script backing — this is a prompt-driven discipline; the only filesystem effects are the brain write and the appended stamp line.
