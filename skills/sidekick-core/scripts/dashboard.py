#!/usr/bin/env python3
"""Build a self-contained Sidekick dashboard HTML from a small SK-data JSON.

The agent NEVER reads or pastes the ~11 KB UI kernel — this script reads
assets/ui.css + ui.js + solidbricks.png from disk (full, native, no context
truncation) and bakes the complete page. The only thing the agent edits per
dashboard is the tiny  dashboard/<slug>-dashboard.sk.json  data file.

The .sk.json holds LAYOUT + DATA BINDINGS, not hardcoded numbers: an element
may carry a `query` (a read-only SELECT) or `recipe` (a name in .reports.json)
instead of literal values. At build time `_resolve_bindings` runs each query
NATIVELY via data.py and bakes the FRESH rows into the html — so the dashboard
is a live view of the data store, never a stale snapshot the agent hand-edits.
Alias your SELECT columns to the field names the renderer reads (label/value/
color for a chart; the grid/table column keys; value/delta/sub/tone for a KPI;
primary/secondary/meta for a panel item). Elements with no binding keep their
literal values (older hand-authored dashboards still build unchanged).

Why a script: pasting the kernel inline made Cowork's agent-read truncate it
(~11.4 KB), producing blank dashboards. A native read sidesteps that entirely.

Layout (one dashboard per project; new one only on explicit request):
  <project>/dashboard/<slug>-dashboard.sk.json   <- source of truth (agent edits).
                                          In a LOCAL, NON-synced subfolder: not the
                                          project root (untidy, sits next to agenda/
                                          etc.) and NOT artifacts/, which is
                                          Drive-synced and whose files can be
                                          cloud-only placeholders (stat ok, open
                                          fails); dashboard/ is local, so reads here
                                          are reliable.
  <project>/artifacts/<slug>-dashboard.html   <- built output (synced to Drive).
                                          dashboard.py only WRITES it; never read it
                                          back (a placeholder open would fail) — the
                                          live wrapper loads it from Drive.

Usage:
  dashboard.py build  --project <ABS_PROJECT_DIR> --slug <slug> [--title "<T>"]
  dashboard.py path   --project <ABS_PROJECT_DIR> --slug <slug>   # print out path

--project must be the ABSOLUTE project dir (Cowork's CLAUDE_PROJECT_DIR is a
scratchpad, not the workspace — same rule as the sync tools).
"""
import argparse, base64, json, sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _skeleton(title):
    """An empty-but-valid dashboard: branded shell, one placeholder collection."""
    return {
        "workspace": title,
        "theme": "paper",
        "accent": "blue",
        "collections": [
            {
                "id": "overview", "label": "Overview", "icon": "layout",
                "section": "top", "home": True,
                "greeting": title,
                "intro": "Nog leeg — vraag Sidekick om hier cijfers, lijsten of "
                         "grafieken op te nemen.",
                "kpis": [], "panels": [],
            }
        ],
    }


def _concat(glob_pat):
    """Read + join the kit chunks (ui.1.css, ui.2.css, … / ui.1.js, ui.2.js, …).

    The kit is shipped in <9 KB chunks because Cowork's `.remote-plugins` mount
    truncates a script-read of a larger file (~11 KB observed: a 12 KB ui.js came
    back at 11421 B). Each small chunk reads whole; we join in numeric order.
    """
    parts = sorted(ASSETS.glob(glob_pat),
                   key=lambda p: int(p.name.split(".")[1]))
    if not parts:
        raise RuntimeError("no %s chunks found in %s — reinstall the plugin." % (glob_pat, ASSETS))
    return "".join(p.read_text(encoding="utf-8") for p in parts)


def _assemble(data):
    css = _concat("ui.*.css")
    js = _concat("ui.*.js")
    # Truncation guard. If a chunk still came back short (flaky mount), baking a
    # partial kernel renders a BLANK page — so verify the end-sentinels and raise
    # instead of writing a broken dashboard. (Kernel must end with `render();`,
    # the CSS with a closing brace.)
    if not js.rstrip().endswith("render();"):
        raise RuntimeError("ui.js chunks assembled short (%d B; must end with 'render();') "
                           "— a plugin file was truncated on read; retry or reinstall."
                           % len(js.encode("utf-8")))
    if len(css) < 4000 or not css.rstrip().endswith("}"):
        raise RuntimeError("ui.css chunks assembled short (%d B) — a plugin file was "
                           "truncated on read; retry or reinstall." % len(css.encode("utf-8")))
    logo = ""
    png = ASSETS / "solidbricks.png"
    if png.exists():
        logo = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode("ascii")
    lang = data.get("lang", "en")
    title = data.get("workspace", "Dashboard")
    sk = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        '<!doctype html><html lang="' + lang + '" data-theme="'
        + data.get("theme", "paper") + '"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>" + _esc(title) + "</title>\n<style>\n" + css + "\n</style></head>\n"
        '<body data-accent="' + data.get("accent", "blue") + '">'
        '<div id="root" class="app"></div>\n'
        "<script>window.SB_LOGO=" + json.dumps(logo) + ";</script>\n"
        "<!-- DATA: this dashboard's only editable part is the matching\n"
        "     dashboard/<slug>-dashboard.sk.json — edit that and re-run dashboard.py build. -->\n"
        "<script>window.SK=" + sk + ";</script>\n"
        "<script>\n" + js + "\n</script>\n</body></html>\n"
    )


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _paths(project, slug):
    proj = Path(project)
    # editable source in a LOCAL, non-synced subfolder (dashboard/) — reliable
    # read. NOT the project root (untidy) and NOT the Drive-synced artifacts/,
    # whose files can be cloud-only placeholders (open fails). html in artifacts/.
    return (proj / "artifacts",
            proj / "dashboard" / (slug + "-dashboard.sk.json"),
            proj / "artifacts" / (slug + "-dashboard.html"))


def _unbind(el):
    el.pop("query", None)
    el.pop("recipe", None)


def _resolve_bindings(project, sk):
    """Replace `query`/`recipe` bindings in the SK object with LIVE data, in
    place. Each bound element aliases its SELECT columns to the field names the
    renderer reads. This makes the dashboard a live view of the data store
    (single source of truth = the query), not a hand-edited snapshot. Raises
    RuntimeError (naming the failing query) so a bad binding is LOUD, never a
    silently stale page."""
    # data.py / reports.py are siblings; import lazily so a binding-free build
    # never depends on them.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import data as data_mod
    try:
        import reports as reports_mod
    except Exception:
        reports_mod = None

    def rows_for(el):
        try:
            if el.get("recipe"):
                if reports_mod is None:
                    raise RuntimeError("a `recipe` binding needs reports.py")
                return reports_mod.run(project, el["recipe"]).get("rows", [])
            return data_mod.query(project, el["query"]).get("rows", [])
        except Exception as e:
            ref = el.get("recipe") and ("recipe " + el["recipe"]) or el.get("query")
            raise RuntimeError("dashboard binding failed (%s): %s" % (ref, e))

    def bound(el):
        return isinstance(el, dict) and ("query" in el or "recipe" in el)

    def resolve(node):
        if not isinstance(node, dict):
            return
        for kpi in node.get("kpis", []) or []:          # KPI strip / home kpis
            if bound(kpi):
                r = rows_for(kpi)
                if r:
                    kpi.update(r[0])                    # first row → kpi fields
                _unbind(kpi)
        for card in node.get("cards", []) or []:        # dashboard cards
            ch, tb = card.get("chart"), card.get("table")
            if bound(ch):
                ch["data"] = rows_for(ch); _unbind(ch)
            if bound(tb):
                tb["rows"] = rows_for(tb); _unbind(tb)
        for panel in node.get("panels", []) or []:      # home panels
            if bound(panel):
                panel["items"] = rows_for(panel); _unbind(panel)
        if node.get("kind") == "grid" and bound(node):  # grid view
            node["rows"] = rows_for(node); _unbind(node)
        if node.get("kind") == "listdetail" and bound(node):
            node["items"] = rows_for(node); _unbind(node)
        if node.get("totals_query"):                    # grid totals row
            tr = data_mod.query(project, node["totals_query"]).get("rows", [])
            node.pop("totals_query")
            if tr:
                node["totals"] = tr[0]

    for col in sk.get("collections", []) or []:
        resolve(col)                                    # collection home (kpis/panels)
        for view in col.get("views", []) or []:
            resolve(view)


def build(project, slug, title=None):
    """Build (or skeleton) a project's dashboard. Resolves any `query`/`recipe`
    bindings against the live data store before baking. Returns a result dict
    (incl. `changed`: did the html actually move vs the prior build); raises
    RuntimeError on bad input, a truncated asset, or a failing binding — so both
    the CLI and the `sidekick-sync` MCP server (which runs NATIVELY, with
    reliable filesystem access) handle it the same way. Building via the MCP
    server sidesteps the sandbox bash mount that truncates script-reads."""
    if not Path(project).is_absolute():
        raise RuntimeError("project must be an ABSOLUTE path (got: %s)" % project)
    art, data_path, html_path = _paths(project, slug)
    art.mkdir(parents=True, exist_ok=True)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    # Migrate a legacy root-level sk.json (pre-v0.16.0) into dashboard/ so an
    # existing dashboard keeps its content after the move.
    legacy = Path(project) / (slug + "-dashboard.sk.json")
    if legacy.exists() and not data_path.exists():
        # utf-8-sig tolerates a BOM (e.g. a sk.json written by a Windows editor).
        data_path.write_text(legacy.read_text(encoding="utf-8-sig"), encoding="utf-8")
        try:
            legacy.unlink()
        except OSError:
            pass
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding="utf-8-sig"))
        if title:
            data["workspace"] = title
    else:
        data = _skeleton(title or (slug.replace("-", " ").title() + " Dashboard"))
        data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _resolve_bindings(project, data)   # pull live query/recipe results into the SK
    new_html = _assemble(data)
    try:
        prev = html_path.read_text(encoding="utf-8") if html_path.exists() else None
    except OSError:
        prev = None                    # placeholder/unhydrated — can't compare
    changed = new_html != prev
    html_path.write_text(new_html, encoding="utf-8")
    return {"data": str(data_path), "html": str(html_path),
            "collections": len(data.get("collections", [])), "changed": changed}


def _dashboard_slugs(project):
    """Every dashboard slug in a project — the dashboard/ subfolder plus any
    legacy root-level sk.json (build() migrates the latter)."""
    proj, suffix, slugs = Path(project), "-dashboard.sk.json", set()
    for f in (proj / "dashboard").glob("*" + suffix):
        slugs.add(f.name[:-len(suffix)])
    for f in proj.glob("*" + suffix):
        slugs.add(f.name[:-len(suffix)])
    return sorted(slugs)


def build_all(project):
    """Rebuild EVERY dashboard in a project (used after a data change, so the
    one tool call refreshes all affected dashboards). Each keeps its own title.
    Returns per-dashboard results + whether any html actually changed."""
    if not Path(project).is_absolute():
        raise RuntimeError("project must be an ABSOLUTE path (got: %s)" % project)
    built = [build(project, slug) for slug in _dashboard_slugs(project)]
    return {"ok": True, "count": len(built), "built": built,
            "any_changed": any(b.get("changed") for b in built)}


def cmd_build(a):
    try:
        out = build(a.project, a.slug, a.title) if a.slug \
            else build_all(a.project)
        print(json.dumps(out))
    except RuntimeError as e:
        sys.exit("ERROR: " + str(e))


def cmd_path(a):
    _, data_path, html_path = _paths(a.project, a.slug)
    print(json.dumps({"data": str(data_path), "html": str(html_path)}))


def main():
    p = argparse.ArgumentParser(description="Build a Sidekick dashboard HTML.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("build", "path"):
        s = sub.add_parser(name)
        s.add_argument("--project", required=True)
        # build with no --slug rebuilds every dashboard in the project.
        s.add_argument("--slug", required=(name == "path"), default=None)
        if name == "build":
            s.add_argument("--title", default=None)
    a = p.parse_args()
    {"build": cmd_build, "path": cmd_path}[a.cmd](a)


if __name__ == "__main__":
    main()
