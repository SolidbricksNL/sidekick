#!/usr/bin/env python3
"""Sidekick report-recipe registry. Stores named, reusable report recipes
(name -> SELECT) in <project>/.reports.json and runs them via data.py's query
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
    return Path(project) / ".reports.json"


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
    _path(project).write_text(json.dumps(reg, ensure_ascii=False, indent=2),
                              encoding="utf-8")


def save(project, name, sql, desc=""):
    """Add/replace a recipe. The SQL must be a read-only SELECT (enforced when
    it runs). Mirror it in brain/reports.md separately (gated, plain-language)."""
    if not _NAME.match(name):
        raise ValueError(f"invalid report name {name!r} "
                         "(letters, digits, _ and -, not starting with -)")
    reg = _load(project)
    reg[name] = {"sql": sql, "desc": desc}
    _save(project, reg)
    return {"ok": True, "action": "save", "report": name}


def list_reports(project):
    reg = _load(project)
    return {"ok": True, "action": "list",
            "reports": [{"name": n, "desc": v.get("desc", "")}
                        for n, v in sorted(reg.items())]}


def run(project, name):
    """Look up a recipe by name and execute its SELECT via the query engine."""
    reg = _load(project)
    if name not in reg:
        raise ValueError(f"unknown report {name!r} "
                         f"(known: {', '.join(sorted(reg)) or 'none'})")
    res = data.query(project, reg[name]["sql"])
    res["report"] = name
    return res


def cmd_save(args):
    try:
        _emit(save(args.project, args.name, args.sql, args.desc or ""))
    except ValueError as e:
        _die(f"error: {e}")


def cmd_list(args):
    _emit(list_reports(args.project))


def cmd_run(args):
    try:
        _emit(run(args.project, args.name))
    except ValueError as e:
        _die(f"error: {e}")


def build_parser():
    p = argparse.ArgumentParser(prog="reports.py",
                                description="Sidekick report-recipe registry")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="add/replace a named recipe")
    s.add_argument("--project", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--sql", required=True, help="a read-only SELECT")
    s.add_argument("--desc", default="")
    s.set_defaults(func=cmd_save)

    n = sub.add_parser("list", help="list saved recipes")
    n.add_argument("--project", required=True)
    n.set_defaults(func=cmd_list)

    r = sub.add_parser("run", help="run a recipe by name (read-only)")
    r.add_argument("--project", required=True)
    r.add_argument("--name", required=True)
    r.set_defaults(func=cmd_run)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
