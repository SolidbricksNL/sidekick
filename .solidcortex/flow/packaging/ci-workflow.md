---
flowId: packaging
nodeId: ci-workflow
type: integration
slug: ci-workflow
status: current
kind: derived
summary: GitHub Actions workflow that checks out the repo on an external runner and runs the structure validator on every push and pull request, failing the build on any FAIL.
systems: [validation]
domains: [dev-tooling]
parent: main/packaging
mainCodeFile: .github/workflows/validate.yml
edges:
  - to: packaging/structure-validator
    via: starts
    label: runs validator in CI
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** GitHub Actions workflow that checks out the repo on a hosted runner and runs the structure validator on every push and pull request.
**Inputs:** `push` and `pull_request` events; checks out the repo and sets up Node 20.
**Outputs:** A green or failing `validate / structure` check; build fails on any validator FAIL.
**Code anchor:** [.github/workflows/validate.yml](../../../.github/workflows/validate.yml)
**Edges:** → packaging/structure-validator (runs validator in CI)
**Key rules:**
- Triggers on both `push` and `pull_request` (all branches, unfiltered).
- Runs on `ubuntu-latest` with Node 20; a non-zero validator exit fails the job.
- Runs the validator directly with no `npm install` — the script is zero-dependency.

## Functional (user facing)

### Why use this?
It is the backstop that no one can skip. The pre-commit hook is opt-in and can be bypassed with `--no-verify`; this workflow runs the same structural and truncation-cap checks on GitHub's own machines for every push and pull request, so a broken plugin layout can't quietly reach the main branch.

### When it runs
On every push to the repository and on every pull request — automatically, with no manual step.

### What it talks to
GitHub Actions hosted runners. The job spins up a fresh `ubuntu-latest` machine, checks out the code, and installs Node 20 — all from GitHub's standard `actions/checkout` and `actions/setup-node` actions.

### Behind the scenes
The runner is disposable and starts clean each time, which is exactly why the validator needs zero dependencies: there's nothing to install, the script just runs against the freshly checked-out tree. A failed validator turns the check red and blocks the change.

### Pro tips
- This and the pre-commit hook run the identical script, so a local pass predicts a green CI run.
- Check 7's truncation guard is the headline reason this exists in CI: a file can never silently grow past the install cap and lose its tail without the build going red.

### Related
- packaging/structure-validator — the validator this workflow runs.
- packaging/precommit-hook — the local-side guard running the same check earlier.

## Technical
- **Main file:** `.github/workflows/validate.yml` — GitHub Actions workflow named `validate`, ~21 lines.
- **Triggers:** `on: { push, pull_request }` with no branch or path filters — every push and PR.
- **Job `structure`:** `runs-on: ubuntu-latest`; steps are `actions/checkout@v4`, `actions/setup-node@v4` with `node-version: '20'`, then a single run step `node scripts/validate-structure.mjs`.
- **No install step:** there is deliberately no `npm ci`/`npm install` — `packaging/structure-validator` is stdlib-only, so the checkout + node-setup is sufficient.
- **Failure semantics:** the run step inherits the validator's exit code; a non-zero exit fails the step and the job, marking the commit/PR check red.
- **Dependencies:** external GitHub Actions infrastructure (the integration boundary); delegates all checks to `packaging/structure-validator`, the same script wrapped locally by `packaging/precommit-hook`.

