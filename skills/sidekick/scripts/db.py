#!/usr/bin/env python3
"""Sidekick per-project SQLite helper.

Sidekick stores genuinely structured project data in one SQLite file per
project at `projects/<slug>/data.sqlite`. The `sqlite3` CLI is not guaranteed
in Cowork, so all database work goes through this stdlib-only helper
(Python 3.11+ confirmed in-env). No external dependencies.

This helper executes SQL; it does NOT enforce the gatekeeper. The skill is
responsible for getting plain-language approval BEFORE calling `schema`
(create/alter/drop). `insert` and `query` are free per the write disciplines:
records that fit the schema flow in freely, and reads never mutate.

Subcommands
-----------
  schema  --db PATH --sql "<DDL>"            run one approved structure change
  insert  --db PATH --table NAME --json ROWS insert records (JSON array of objects)
  query   --db PATH --sql "<SELECT>"         run a read-only query (read-only conn)
  info    --db PATH                          list tables + columns (for extend-before-add)

All subcommands print a JSON result to stdout and exit non-zero on error
(message on stderr). `schema` lazily creates the database file (and its parent
directory) on first use — this is the lazy-creation point for `data.sqlite`.

Examples
--------
  python3 db.py schema --db projects/acme/data.sqlite \
      --sql "CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT, company TEXT, role TEXT, email TEXT)"
  python3 db.py insert --db projects/acme/data.sqlite --table contacts \
      --json '[{"name":"Ada Lovelace","company":"Analytical","role":"Engineer","email":"ada@ex.com"}]'
  python3 db.py query  --db projects/acme/data.sqlite \
      --sql "SELECT name, company FROM contacts WHERE email IS NULL"
  python3 db.py info   --db projects/acme/data.sqlite
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# SQLite identifiers we are willing to interpolate (table/column names cannot be
# bound as parameters). Anything outside this shape is rejected, not quoted.
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def _check_ident(name, kind):
    if not _IDENT.match(name):
        _die(f"error: invalid {kind} name {name!r} "
             f"(allowed: letters, digits, underscore; must not start with a digit)")
    return name


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def cmd_schema(args):
    """Run one approved structure change. Lazily creates the DB + parent dir."""
    db = Path(args.db)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(args.sql)  # single statement; the skill supplies vetted DDL
        conn.commit()
    except sqlite3.Error as e:
        _die(f"error: schema change failed: {e}")
    finally:
        conn.close()
    _emit({"ok": True, "action": "schema", "db": str(db)})


def cmd_insert(args):
    """Insert records that fit an existing table. Parameterized, no gatekeeper."""
    table = _check_ident(args.table, "table")
    try:
        rows = json.loads(args.json)
    except json.JSONDecodeError as e:
        _die(f"error: --json is not valid JSON: {e}")
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list) or not rows:
        _die("error: --json must be a non-empty object or array of objects")

    cols = list(rows[0].keys())
    if not cols:
        _die("error: rows have no columns")
    for c in cols:
        _check_ident(c, "column")
    # Every row must share the same column set so executemany is well-formed.
    for i, r in enumerate(rows):
        if list(r.keys()) != cols:
            _die(f"error: row {i} has different columns than the first row")

    placeholders = ",".join("?" * len(cols))
    collist = ",".join(cols)
    sql = f"INSERT INTO {table} ({collist}) VALUES ({placeholders})"
    values = [[r[c] for c in cols] for r in rows]

    db = Path(args.db)
    if not db.exists():
        _die(f"error: database {db} does not exist — create the table first (schema)")
    conn = sqlite3.connect(str(db))
    try:
        cur = conn.executemany(sql, values)
        conn.commit()
        inserted = cur.rowcount
    except sqlite3.Error as e:
        _die(f"error: insert failed: {e}")
    finally:
        conn.close()
    _emit({"ok": True, "action": "insert", "table": table, "inserted": inserted})


def cmd_query(args):
    """Run a read-only query. Connection is opened read-only so it cannot mutate."""
    db = Path(args.db)
    if not db.exists():
        _die(f"error: database {db} does not exist")
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(args.sql)
        rows = [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as e:
        _die(f"error: query failed: {e}")
    finally:
        try:
            conn.close()
        except NameError:
            pass
    _emit({"ok": True, "action": "query", "rowcount": len(rows), "rows": rows})


def cmd_info(args):
    """List tables and their columns — supports the extend-before-add rule and
    lets the skill regenerate brain/data-model.md from the live schema."""
    db = Path(args.db)
    if not db.exists():
        _emit({"ok": True, "action": "info", "db": str(db), "exists": False, "tables": []})
        return
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        names = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        tables = []
        for name in names:
            cols = [{"name": c[1], "type": c[2], "notnull": bool(c[3]),
                     "pk": bool(c[5])}
                    for c in conn.execute(f"PRAGMA table_info({_check_ident(name, 'table')})")]
            tables.append({"name": name, "columns": cols})
    except sqlite3.Error as e:
        _die(f"error: info failed: {e}")
    finally:
        conn.close()
    _emit({"ok": True, "action": "info", "db": str(db), "exists": True, "tables": tables})


def build_parser():
    p = argparse.ArgumentParser(prog="db.py", description="Sidekick SQLite helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("schema", help="run one approved structure change (DDL)")
    s.add_argument("--db", required=True)
    s.add_argument("--sql", required=True)
    s.set_defaults(func=cmd_schema)

    i = sub.add_parser("insert", help="insert records that fit the schema")
    i.add_argument("--db", required=True)
    i.add_argument("--table", required=True)
    i.add_argument("--json", required=True, help="JSON object or array of objects")
    i.set_defaults(func=cmd_insert)

    q = sub.add_parser("query", help="run a read-only query")
    q.add_argument("--db", required=True)
    q.add_argument("--sql", required=True)
    q.set_defaults(func=cmd_query)

    n = sub.add_parser("info", help="list tables and columns")
    n.add_argument("--db", required=True)
    n.set_defaults(func=cmd_info)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
