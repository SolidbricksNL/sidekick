---
flowId: sidekick-sync
nodeId: save-report
slug: save-report
status: current
kind: derived
summary: The save_report tool — registers or merges an entry in the project's .sidekick/reports.json recipe registry, validating the name and writing either a query recipe (named SELECT) or a sql-less dashboard registration.
systems: [mcp-server]
domains: [reporting]
parent: sidekick-sync/mcp-server
generatedFromSha: 220126f8a916c8cc7e9b3608c2c68c1e8ad94466
generatedAt: 2026-06-14T11:55:56Z
generator: solidcortex@0.17.0
---

## Technical

**Entry point.** The `save_report` MCP tool is declared in `skills/sidekick-core/scripts/sync_server.py` (`_TOOLS[3]`) and dispatched as `reports.save(proj, args["name"], args.get("sql"), args.get("desc"), args.get("artifact"), args.get("drive_file_id"), args.get("tables"))`, wrapped in `_ok`. Input schema requires `project` and `name`; `sql`, `desc`, `artifact`, `drive_file_id`, `tables` are optional. A `ValueError` (bad name / empty new entry) surfaces as an MCP tool error.

**Main code.** `skills/sidekick-core/scripts/reports.py` (~191 LOC) — the report-recipe registry. Besides `save` it exposes `list_reports`, `uses`, and `run`, plus a CLI (`reports.py save|list|run|uses`); the MCP path uses only `save` (and `run`, indirectly, via dashboard binding resolution).

**Storage + migration.** `_path(project)` resolves `<project>/.sidekick/reports.json`, migrating a legacy root-level `.reports.json` into `.sidekick/` on first access. `_load` returns the dict (or `{}` on missing/corrupt JSON); `_save` writes it `utf-8`, `indent=2`, `ensure_ascii=False`.

**`save(project, name, sql, desc, artifact, drive_file_id, tables)`.** Validates `name` against `_NAME = ^[A-Za-z0-9][A-Za-z0-9_-]*$` (raises `ValueError` otherwise). Loads the registry, takes `entry = reg.get(name, {})`, and merges field-by-field over `("sql","desc","artifact","drive_file_id","tables")` — only non-`None` values overwrite, so a later call can add `drive_file_id` without resending `sql`. A brand-new entry that ends up empty raises `ValueError` ("give it at least a `sql` … or `artifact`/`drive_file_id`"). Persists and returns `{ok, action:"save", report:name, entry}`.

**Entry kinds.** By design an entry is EITHER a query recipe (a single named read-only `SELECT` in `sql`) OR a dashboard registration (`artifact` + `drive_file_id` + `tables`, no sql). A report with several named sub-queries maps to one recipe entry per sub-query, not one entry with a representative sql; the dashboard itself is its own sql-less entry. `run(project, name)` raises if an entry has no `sql` ("it's a dashboard/artifact registration, not a query recipe").

**Related registry surface (not MCP-exposed).** `run` executes a recipe's SELECT via `data.query` (sibling `data.py`, read-only SQLite over the project tables) and tags the result with `report:name` — this is what `build_dashboard`'s `_resolve_bindings` calls for a `recipe`-bound tile (see sidekick-sync/build-dashboard). `uses(project, table)` returns recipe names that read a given table (for regenerating on a data change); `list_reports` enumerates entries.

**Dependencies.** Sibling `data.py` (query engine) for `run`. The human-readable mirror of each recipe lives in `brain/reports.md` and is approved as a brain write. Rationale (recipe-vs-artifact split, native save vs sandbox-mount truncation, registry as the live-artifact's source of names) in `docs/ARCHITECTURE.md` §7b.
