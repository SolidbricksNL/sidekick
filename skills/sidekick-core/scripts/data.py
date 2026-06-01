#!/usr/bin/env python3
"""Sidekick structured-data helper. JSON files (one per table) under
<project>/data/ + _schema.json. query runs over a throwaway in-memory SQLite
(never touches disk); writes snapshot first. Protocol: data-discipline.md.
Keep this file small - Cowork truncates large plugin files on install."""

import argparse
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")  # legal table/column names
_TYPES = {"text", "number", "integer", "real", "bool", "boolean", "date"}
_SNAPSHOT_KEEP = 20
_ENUM_MAX = 12  # columns with <= this many distinct values are categorical


def _die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _ident(name, kind):
    if not _IDENT.match(name):
        _die(f"error: invalid {kind} name {name!r} "
             f"(allowed: letters, digits, underscore; not starting with a digit)")
    return name


def _ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def _data_dir(project):
    return Path(project) / "data"


def _schema_path(project):
    return _data_dir(project) / "_schema.json"


def _table_path(project, table):
    return _data_dir(project) / f"{table}.json"


def _load_schema(project):
    p = _schema_path(project)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _die(f"error: {p} is not valid JSON: {e}")


def _save_schema(project, schema):
    p = _schema_path(project)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_rows(project, table):
    p = _table_path(project, table)
    if not p.exists():
        _die(f"error: table {table!r} does not exist (create it first)")
    try:
        rows = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _die(f"error: {p} is not valid JSON: {e}")
    if not isinstance(rows, list):
        _die(f"error: {p} must hold a JSON array of objects")
    return rows


def _write_rows(project, table, rows):
    p = _table_path(project, table)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def _snapshot(project, table):
    # Pre-mutation copy into .snapshots/. Best-effort: a sandbox that blocks
    # the copy or prune must never abort the write.
    src = _table_path(project, table)
    if not src.exists():
        return
    try:
        snap_dir = _data_dir(project) / ".snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, snap_dir / f"{table}-{_ts()}.json")
    except OSError as e:
        print(f"warning: snapshot of {table!r} skipped ({e})", file=sys.stderr)
        return
    try:
        for old in sorted(snap_dir.glob(f"{table}-*.json"))[:-_SNAPSHOT_KEEP]:
            try:
                old.unlink()
            except OSError as e:
                print(f"warning: could not prune {old.name} ({e})", file=sys.stderr)
    except OSError:
        pass


def _table_columns(project, table, schema=None):
    # Columns from the schema sidecar, else inferred from the rows' keys.
    schema = schema if schema is not None else _load_schema(project)
    if table in schema:
        return [c["name"] for c in schema[table]["columns"]]
    cols, seen = [], set()
    for r in _load_rows(project, table):
        for k in r:
            if k not in seen:
                seen.add(k)
                cols.append(k)
    return cols


def cmd_create(args):
    table = _ident(args.table, "table")
    schema = _load_schema(args.project)
    if table in schema or _table_path(args.project, table).exists():
        _die(f"error: table {table!r} already exists - use addcol to extend it, "
             f"do not recreate (that would discard data)")
    cols = []
    for spec in args.columns.split(","):
        spec = spec.strip()
        if not spec:
            continue
        if ":" in spec:
            name, typ = spec.split(":", 1)
            name, typ = name.strip(), typ.strip().lower()
        else:
            name, typ = spec, "text"
        _ident(name, "column")
        if typ not in _TYPES:
            _die(f"error: unknown type {typ!r} for column {name!r} "
                 f"(allowed: {', '.join(sorted(_TYPES))})")
        cols.append({"name": name, "type": typ})
    if not cols:
        _die("error: --columns must list at least one column, "
             "e.g. 'name:text,amount:number'")
    schema[table] = {"columns": cols, "created": _ts()}
    _save_schema(args.project, schema)
    _write_rows(args.project, table, [])
    _emit({"ok": True, "action": "create", "table": table,
           "columns": [c["name"] for c in cols]})


def cmd_addcol(args):
    table = _ident(args.table, "table")
    column = _ident(args.column, "column")
    typ = (args.type or "text").lower()
    if typ not in _TYPES:
        _die(f"error: unknown type {typ!r} (allowed: {', '.join(sorted(_TYPES))})")
    schema = _load_schema(args.project)
    if table not in schema:
        _die(f"error: table {table!r} not in schema - create it first")
    if any(c["name"] == column for c in schema[table]["columns"]):
        _die(f"error: column {column!r} already exists on {table!r}")
    _snapshot(args.project, table)
    schema[table]["columns"].append({"name": column, "type": typ})
    _save_schema(args.project, schema)
    rows = _load_rows(args.project, table)
    for r in rows:
        r.setdefault(column, None)
    _write_rows(args.project, table, rows)
    _emit({"ok": True, "action": "addcol", "table": table, "column": column})


def _match_idx(rows, match):
    return [i for i, r in enumerate(rows)
            if all(r.get(k) == v for k, v in match.items())]


def cmd_insert(args):
    table = _ident(args.table, "table")
    try:
        new = json.loads(args.json)
    except json.JSONDecodeError as e:
        _die(f"error: --json is not valid JSON: {e}")
    if isinstance(new, dict):
        new = [new]
    if not isinstance(new, list) or not new:
        _die("error: --json must be a non-empty object or array of objects")
    schema = _load_schema(args.project)
    if table not in schema and not _table_path(args.project, table).exists():
        _die(f"error: table {table!r} does not exist - create it first")
    allowed = set(_table_columns(args.project, table, schema)) if table in schema else None
    for i, r in enumerate(new):
        if not isinstance(r, dict):
            _die(f"error: row {i} is not an object")
        if allowed is not None:
            unknown = [k for k in r if k not in allowed]
            if unknown:
                _die(f"error: row {i} has unknown column(s) {unknown} - "
                     f"add them with addcol first (extend before you add)")
    _snapshot(args.project, table)
    rows = _load_rows(args.project, table)
    if allowed is not None:
        for r in new:
            for c in allowed:
                r.setdefault(c, None)
    rows.extend(new)
    _write_rows(args.project, table, rows)
    _emit({"ok": True, "action": "insert", "table": table,
           "inserted": len(new), "total": len(rows)})


def cmd_update(args):
    table = _ident(args.table, "table")
    try:
        match = json.loads(args.match)
        setvals = json.loads(args.set)
    except json.JSONDecodeError as e:
        _die(f"error: --match/--set is not valid JSON: {e}")
    if not isinstance(match, dict) or not isinstance(setvals, dict) or not setvals:
        _die("error: --match must be an object and --set a non-empty object")
    rows = _load_rows(args.project, table)
    idx = _match_idx(rows, match)
    if not idx:
        _emit({"ok": True, "action": "update", "table": table, "updated": 0})
        return
    _snapshot(args.project, table)
    for i in idx:
        rows[i].update(setvals)
    _write_rows(args.project, table, rows)
    _emit({"ok": True, "action": "update", "table": table, "updated": len(idx)})


def cmd_delete(args):
    table = _ident(args.table, "table")
    try:
        match = json.loads(args.match)
    except json.JSONDecodeError as e:
        _die(f"error: --match is not valid JSON: {e}")
    if not isinstance(match, dict) or not match:
        _die("error: --match must be a non-empty object (refusing to delete every row)")
    rows = _load_rows(args.project, table)
    idx = set(_match_idx(rows, match))
    if not idx:
        _emit({"ok": True, "action": "delete", "table": table, "deleted": 0})
        return
    _snapshot(args.project, table)
    kept = [r for i, r in enumerate(rows) if i not in idx]
    _write_rows(args.project, table, kept)
    _emit({"ok": True, "action": "delete", "table": table,
           "deleted": len(idx), "remaining": len(kept)})


def _sqlval(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool):
        return 1 if v else 0
    return v


def cmd_query(args):
    # SELECT over a throwaway in-memory SQLite; on-disk JSON is never touched.
    sql = args.sql.strip().rstrip(";").strip()
    if not (sql.lstrip("(").lower().startswith(("select", "with"))):
        _die("error: query only runs SELECT statements (reads). "
             "Use insert/update/delete to change data.")
    data_dir = _data_dir(args.project)
    if not data_dir.exists():
        _die(f"error: no data/ for project {args.project!r}")
    schema = _load_schema(args.project)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for f in sorted(data_dir.glob("*.json")):
        if f.name == "_schema.json":
            continue
        table = f.stem
        if not _IDENT.match(table):
            continue
        rows = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        cols = _table_columns(args.project, table, schema)
        if not cols:
            continue
        collist = ",".join(f'"{c}"' for c in cols)
        conn.execute(f'CREATE TABLE "{table}" ({collist})')
        ph = ",".join("?" * len(cols))
        conn.executemany(f'INSERT INTO "{table}" ({collist}) VALUES ({ph})',
                         [[_sqlval(r.get(c)) for c in cols] for r in rows])
    try:
        out = [dict(r) for r in conn.execute(sql).fetchall()]
    except sqlite3.Error as e:
        _die(f"error: query failed: {e}")
    finally:
        conn.close()
    _emit({"ok": True, "action": "query", "rowcount": len(out), "rows": out})


def _distinct_values(rows, name):
    # Distinct non-null values, or None if more than _ENUM_MAX (high-card).
    out, seen = [], set()
    for r in rows:
        v = r.get(name)
        if v is None:
            continue
        key = v if isinstance(v, (str, int, float, bool)) else json.dumps(v, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
        if len(out) > _ENUM_MAX:
            return None
    return sorted(out, key=lambda x: str(x)) if out else None


def cmd_info(args):
    data_dir = _data_dir(args.project)
    if not data_dir.exists():
        _emit({"ok": True, "action": "info", "project": args.project,
               "exists": False, "tables": []})
        return
    schema = _load_schema(args.project)
    tables = []
    for f in sorted(data_dir.glob("*.json")):
        if f.name == "_schema.json":
            continue
        table = f.stem
        rows = json.loads(f.read_text(encoding="utf-8"))
        rows = rows if isinstance(rows, list) else []
        base = (schema[table]["columns"] if table in schema
                else [{"name": c, "type": "text"}
                      for c in _table_columns(args.project, table, schema)])
        cols = []
        for c in base:
            col = dict(c)
            # Categorical columns carry their distinct values so the model
            # matches exact spellings (e.g. "ON-PREM", not "ONPREM").
            vals = _distinct_values(rows, c["name"])
            if vals is not None:
                col["values"] = vals
            cols.append(col)
        tables.append({"name": table, "columns": cols, "rowcount": len(rows)})
    _emit({"ok": True, "action": "info", "project": args.project,
           "exists": True, "tables": tables})


def cmd_backup(args):
    # Timestamped copy of the data/ tables + schema (made by the check-in).
    data_dir = _data_dir(args.project)
    if not data_dir.exists():
        _emit({"ok": True, "action": "backup", "project": args.project,
               "exists": False, "backup": None})
        return
    label = f"-{args.label}" if args.label else ""
    dest = data_dir / ".backups" / f"{_ts()}{label}"
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for f in sorted(data_dir.glob("*.json")):
        shutil.copy2(f, dest / f.name)
        copied.append(f.name)
    _emit({"ok": True, "action": "backup", "project": args.project,
           "backup": str(dest), "files": copied})


def build_parser():
    p = argparse.ArgumentParser(prog="data.py",
                                description="Sidekick file-based data helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="create a table (structure change)")
    c.add_argument("--project", required=True)
    c.add_argument("--table", required=True)
    c.add_argument("--columns", required=True,
                   help="comma list, e.g. 'name:text,amount:number'")
    c.set_defaults(func=cmd_create)

    a = sub.add_parser("addcol", help="add a column (structure change)")
    a.add_argument("--project", required=True)
    a.add_argument("--table", required=True)
    a.add_argument("--column", required=True)
    a.add_argument("--type", default="text")
    a.set_defaults(func=cmd_addcol)

    i = sub.add_parser("insert", help="append records that fit the columns")
    i.add_argument("--project", required=True)
    i.add_argument("--table", required=True)
    i.add_argument("--json", "--rows", "--row", dest="json", required=True, metavar="JSON",
                   help="a JSON object, OR a JSON array for a batch insert "
                        "(preferred: one call, one snapshot)")
    i.set_defaults(func=cmd_insert)

    u = sub.add_parser("update", help="update rows matching --match")
    u.add_argument("--project", required=True)
    u.add_argument("--table", required=True)
    u.add_argument("--match", required=True, help="JSON object of column=value")
    u.add_argument("--set", required=True, help="JSON object of column=value")
    u.set_defaults(func=cmd_update)

    d = sub.add_parser("delete", help="delete rows matching --match")
    d.add_argument("--project", required=True)
    d.add_argument("--table", required=True)
    d.add_argument("--match", required=True, help="JSON object of column=value")
    d.set_defaults(func=cmd_delete)

    q = sub.add_parser("query", help="read-only SELECT over the tables")
    q.add_argument("--project", required=True)
    q.add_argument("--sql", required=True)
    q.set_defaults(func=cmd_query)

    n = sub.add_parser("info", help="list tables, columns (with category values), counts")
    n.add_argument("--project", required=True)
    n.set_defaults(func=cmd_info)

    b = sub.add_parser("backup", help="timestamped copy of data/ (check-in)")
    b.add_argument("--project", required=True)
    b.add_argument("--label", default=None)
    b.set_defaults(func=cmd_backup)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
