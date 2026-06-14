---
flowId: packaging
nodeId: precommit-hook
type: process
slug: precommit-hook
status: current
kind: derived
summary: Local pre-commit hook that runs the structure validator and blocks the commit when it fails, guarding the install-truncation cap before code ever leaves the clone.
systems: [validation]
domains: [dev-tooling]
parent: main/packaging
mainCodeFile: scripts/hooks/pre-commit
edges:
  - to: packaging/structure-validator
    via: starts
    label: runs validator before commit
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Local git pre-commit hook that runs the structure validator and blocks the commit if it fails.
**Inputs:** Fires on `git commit` once `git config core.hooksPath scripts/hooks` is set; runs `node scripts/validate-structure.mjs`.
**Outputs:** Exit 0 (commit proceeds) or exit 1 with the validator output + a blocked-commit message.
**Code anchor:** [scripts/hooks/pre-commit](../../../scripts/hooks/pre-commit)
**Edges:** → packaging/structure-validator (runs validator before commit)
**Key rules:**
- Activation is opt-in per clone via `git config core.hooksPath scripts/hooks` — not automatic on checkout.
- Non-zero validator exit blocks the commit; emergency override is `git commit --no-verify`.
- POSIX `/bin/sh` script — captures combined stdout+stderr and mirrors the validator exit code.

## Functional (user facing)

### Why use this?
It stops a structurally broken plugin from ever becoming a commit. The biggest risk it guards is the silent install-truncation cliff: a runtime file that grows too large is cut off when Cowork installs it, losing its tail with no error. The hook catches that on your machine, before the bad state leaves your clone.

### What it does
- Runs the full structure validator as part of `git commit`.
- Lets the commit through only when the validator passes clean.
- On failure, prints the validator's findings, an explanation that the commit was blocked, and a reminder of the truncation cap.

### How to use it
1. Clone the repo.
2. Run `git config core.hooksPath scripts/hooks` once to point git at the hook.
3. Commit normally — the check runs automatically each time.

### Pro tips
- This is the earliest guard in the chain; CI runs the same validator later as a backstop for anyone who skipped activation or used `--no-verify`.
- The validator + CI workflow + this hook form a copyable bundle — drop all three into any other skill project to get the same protection.

### Related
- packaging/structure-validator — the validator this hook invokes.
- packaging/ci-workflow — the server-side backstop running the same check.

## Technical
- **Main file:** `scripts/hooks/pre-commit` — `#!/bin/sh` script, ~29 lines.
- **Mechanism:** captures `node scripts/validate-structure.mjs 2>&1` into `out`, saves `$?` into `status`. If `status` is non-zero it echoes `out`, a blocked-commit banner, the truncation-cap reminder, the `--no-verify` override note, and `exit 1`; otherwise it echoes a pass line and `exit 0`.
- **Activation:** git only honors the hook after `core.hooksPath` is set to `scripts/hooks` (the repo does not ship a `.git/hooks` symlink), so it is per-clone opt-in.
- **Dependencies:** requires `node` on PATH; delegates all decision logic to `packaging/structure-validator` (this file is a thin gate that only inspects the exit code). The identical script runs server-side via `packaging/ci-workflow`.

