#!/usr/bin/env python3
"""Sidekick report-recipe registry. Stores named, reusable report recipes
(name -> SELECT) in <project>/.sidekick/reports.json and runs them via data.py's query
engine (SQL over all tables in a throwaway in-memory SQLite - read-only). The
sidekick-data MCP server calls run() so live artifacts can fetch a recipe's
output by name. The human-readable mirror lives in brain/reports.md.
Protocol: reporting.md. Keep this file small - Cowork truncates large plugin
files on install."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data  # noqa: E402  (sibling module: the query engine)

_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")  # report names: slug-ish


def _die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _path(project):
    # State lives in the hidden .sidekick/ folder (not loose in the project
    # root). Migrate a legacy root-level .reports.json on first access.
    proj = Path(project)
    new = proj / ".sidekick" / "reports.json"
    legacy = proj / ".reports.json"
    if legacy.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        try:
            legacy.replace(new)
        except OSError:
            pass
    return new


def _load(project):
    p = _path(project)
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(project, reg):
    p = _path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def save(project, name, sql=None, desc=None, artifact=None,
         drive_file_id=None, tables=None):
    """Add/merge a registry entry. Only the given fields are updated (so you can
    set drive_file_id later, after the dashboard HTML is synced). An entry is
    EITHER a **query recipe** (a single named read-only `SELECT`) OR a
    **dashboard registration** (`artifact` + `drive_file_id` + `tables`, no sql)
    — so a report with several named sub-queries (by_line, by_month, …) maps to
    **one recipe entry per sub-query**, not one entry with a single representative
    sql; the dashboard itself is its own (sql-less) entry. Mirror the human
    version in brain/reports.md separately (gated, plain-language).
      artifact      - relative path of the generated dashboard, e.g. artifacts/<n>.html
      drive_file_id - the Drive file id of that synced HTML (for the wrapper)
      tables        - the data tables it reads (drives regeneration on a change)"""
    if not _NAME.match(name):
        raise ValueError(f"invalid report name {name!r} "
                         "(letters, digits, _ and -, not starting with -)")
    reg = _load(project)
    entry = reg.get(name, {})
    for key, val in (("sql", sql), ("desc", desc), ("artifact", artifact),
                     ("drive_file_id", drive_file_id), ("tables", tables)):
        if val is not None:
            entry[key] = val
    if not entry:
        raise ValueError(f"report {name!r} is new — give it at least a `sql` "
                         "(a query recipe) or `artifact`/`drive_file_id` "
                         "(a dashboard registration).")
    reg[name] = entry
    _save(project, reg)
    return {"ok": True, "action": "save", "report": name, "entry": entry}


def list_reports(project):
    reg = _load(project)
    return {"ok": True, "action": "list",
            "reports": [{"name": n, "desc": v.get("desc", ""),
                         "artifact": v.get("artifact"),
                         "drive_file_id": v.get("drive_file_id"),
                         "tables": v.get("tables", [])}
                        for n, v in sorted(reg.items())]}


def uses(project, table):
    """Report names that read a given table (for regenerating on a data change)."""
    reg = _load(project)
    return {"ok": True, "action": "uses", "table": table,
            "reports": sorted(n for n, v in reg.items()
                              if table in (v.get("tables") or []))}


def run(project, name):
    """Look up a recipe by name and execute its SELECT via the query engine."""
    reg = _load(project)
    if name not in reg:
        raise ValueError(f"unknown report {name!r} "
                         f"(known: {', '.join(sorted(reg)) or 'none'})")
    sql = reg[name].get("sql")
    if not sql:
        raise ValueError(f"report {name!r} has no sql to run "
                         "(it's a dashboard/artifact registration, not a query recipe)")
    res = data.query(project, sql)
    res["report"] = name
    return res


def cmd_save(args):
    tables = [t.strip() for t in args.tables.split(",") if t.strip()] \
        if args.tables is not None else None
    try:
        _emit(save(args.project, args.name, args.sql, args.desc,
                   args.artifact, args.drive_file_id, tables))
    except ValueError as e:
        _die(f"error: {e}")


def cmd_list(args):
    _emit(list_reports(args.project))


def cmd_uses(args):
    _emit(uses(args.project, args.table))


def cmd_run(args):
    try:
        _emit(run(args.project, args.name))
    except ValueError as e:
        _die(f"error: {e}")


def build_parser():
    p = argparse.ArgumentParser(prog="reports.py",
                                description="Sidekick report-recipe registry")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="add/merge a named recipe")
    s.add_argument("--project", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--sql", default=None, help="a read-only SELECT")
    s.add_argument("--desc", default=None)
    s.add_argument("--artifact", default=None, help="dashboard path, e.g. artifacts/<n>.html")
    s.add_argument("--drive-file-id", default=None, help="Drive file id of the synced HTML")
    s.add_argument("--tables", default=None, help="comma list of tables the recipe reads")
    s.set_defaults(func=cmd_save)

    n = sub.add_parser("list", help="list saved recipes")
    n.add_argument("--project", required=True)
    n.set_defaults(func=cmd_list)

    r = sub.add_parser("run", help="run a recipe by name (read-only)")
    r.add_argument("--project", required=True)
    r.add_argument("--name", required=True)
    r.set_defaults(func=cmd_run)

    u = sub.add_parser("uses", help="reports that read a given table")
    u.add_argument("--project", required=True)
    u.add_argument("--table", required=True)
    u.set_defaults(func=cmd_uses)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
