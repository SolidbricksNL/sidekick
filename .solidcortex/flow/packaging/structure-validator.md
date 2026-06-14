---
flowId: packaging
nodeId: structure-validator
type: process
slug: structure-validator
status: current
kind: derived
summary: Zero-dependency Node validator that checks the expected tree, both manifests, skill frontmatter, reference paths, the ~15808-byte install-truncation cap (Check 7), and guide-register coverage (Check 8), exiting non-zero on any FAIL.
systems: [validation]
domains: [dev-tooling]
parent: main/packaging
mainCodeFile: scripts/validate-structure.mjs
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## TLDR (agent)
**Purpose:** Zero-dependency Node script that validates the on-disk plugin layout, both manifests, skill frontmatter, references, the install-truncation cap, and guide-register coverage.
**Inputs:** Run `node scripts/validate-structure.mjs` from the repo; reads the tree, `plugin.json`, `marketplace.json`, every `SKILL.md` + `commands/*.md`, and `skill-register.md`.
**Outputs:** PASS/WARN/FAIL line per check, a summary count, and exit code 0 (clean) or 1 (any FAIL).
**Code anchor:** [scripts/validate-structure.mjs](../../../scripts/validate-structure.mjs)
**Edges:** ← packaging/precommit-hook (runs validator before commit), ← packaging/ci-workflow (runs validator in CI)
**Key rules:**
- Any FAIL → exit 1; WARNs never fail the run.
- Check 7 FAILs any runtime file under `skills/` larger than the 15808-byte cap (warns within ~500 B); `docs/` is exempt.
- Check 2 FAILs a non-string `repository`; Check 8 FAILs any skill missing a guide-register entry (or a register slug with no skill).
- Uses only Node stdlib (`node:fs`, `node:path`, `node:url`) — no npm install.

## Functional (user facing)

### Why use this?
This is the single command that tells you, before you ship, whether the plugin will actually install and behave correctly in Cowork. It catches the failure modes that are otherwise invisible until a user installs: a malformed manifest that silently breaks commands, a reference link that points nowhere, or a file that grows past the size where Cowork truncates it on install.

### What it does
- Confirms every expected file in the plugin tree exists, and that `.claude-plugin/` holds only the two manifests.
- Parses both manifests and checks their required fields, including the string-`repository` rule.
- Verifies each skill's frontmatter name matches its folder, that all `references/...` links resolve, and that every typed `/sidekick-*` command has a backing skill and command file.
- Guards every runtime file under `skills/` against the install-truncation cap.
- Confirms the onboarding guide's register has an entry for every skill and no stale entries.

### Pro tips
- It prints a clear PASS/WARN/FAIL per check, so a failing run points straight at the offending file.
- A WARN is advisory (e.g. a recommended-but-missing manifest field); only a FAIL blocks. The bottom line reads `Result: PASS/FAIL (N fail, M warn)`.
- Run it directly any time; CI and the pre-commit hook run the very same script, so a local pass means a clean build.

### Related
- packaging/precommit-hook — runs this before each commit.
- packaging/ci-workflow — runs this on every push and PR.

## Technical
- **Main file:** `scripts/validate-structure.mjs` — ES-module Node script, ~320 LOC, stdlib-only. `ROOT` is resolved one level up from the script.
- **Checks:** (1) `EXPECTED_TREE` existence + `.claude-plugin/` allow-set; (2) `plugin.json` parse, required `name`, string-`repository` FAIL, recommended/optional field warns; (2b) `marketplace.json` parse, `name`/`owner.name`/`plugins[]`, per-plugin `source` starts-with-`./` and resolves to a `plugin.json`, self-name-vs-`plugin.json` warn; (3) per-skill frontmatter name==folder + description length bounds (warns <20 or >1024 chars); (4) `references/...` link resolution via `REF_RE` (own + cross-skill `../<dir>/`); (5) dead `/sidekick-*` command refs via `CMD_RE`; (6) a `commands/<skill>.md` with matching frontmatter for each `EXPLICIT_SKILLS` entry; (7) truncation cap; (8) guide-register coverage.
- **Constants:** `SKILLS` (9 skill folders, main is `sidekick-core`), `EXPLICIT_SKILLS` (8 command-backed skills), `EXPECTED_TREE`, `TRUNC_CAP = 15808`, `TRUNC_WARN = 15300`.
- **Truncation cap (Check 7):** `walkFiles` recurses `skills/`, skipping `__pycache__`, collecting `.md/.py/.css/.js`; each over `TRUNC_CAP` FAILs (tail truncated on Cowork install), each over `TRUNC_WARN` warns. `docs/` is intentionally not walked (dev-only, never loaded at runtime).
- **Frontmatter parser:** local `parseFrontmatter` reads the leading `---` block into a flat key→value map via a per-line regex (no YAML dependency).
- **Exit contract:** `process.exit(fails === 0 ? 0 : 1)`. Consumed identically by `packaging/precommit-hook` (local) and `packaging/ci-workflow` (CI runner).

