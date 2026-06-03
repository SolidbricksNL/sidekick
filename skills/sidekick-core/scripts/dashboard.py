#!/usr/bin/env python3
"""Build a self-contained Sidekick dashboard HTML from a small SK-data JSON.

The agent NEVER reads or pastes the ~11 KB UI kernel — this script reads
assets/ui.css + ui.js + solidbricks.png from disk (full, native, no context
truncation) and bakes the complete page. The only thing the agent edits per
dashboard is the tiny  artifacts/<slug>-dashboard.sk.json  data file.

Why a script: pasting the kernel inline made Cowork's agent-read truncate it
(~11.4 KB), producing blank dashboards. A native read sidesteps that entirely.

Layout (one dashboard per project; new one only on explicit request):
  <project>/<slug>-dashboard.sk.json   <- source of truth (agent edits) — at the
                                          PROJECT ROOT, NOT in artifacts/. artifacts/
                                          is Drive-synced and its files can be
                                          cloud-only placeholders (stat ok, open
                                          fails); the root is local, so reads here
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
        "     artifacts/<slug>-dashboard.sk.json — edit that and re-run dashboard.py build. -->\n"
        "<script>window.SK=" + sk + ";</script>\n"
        "<script>\n" + js + "\n</script>\n</body></html>\n"
    )


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _paths(project, slug):
    proj = Path(project)
    # data at the project ROOT (local, reliable read — not the Drive-synced
    # artifacts/, whose files can be cloud-only placeholders); html in artifacts/.
    return (proj / "artifacts",
            proj / (slug + "-dashboard.sk.json"),
            proj / "artifacts" / (slug + "-dashboard.html"))


def build(project, slug, title=None):
    """Build (or skeleton) a project's dashboard. Returns a result dict; raises
    RuntimeError on bad input or a truncated asset — so both the CLI and the
    `sidekick-sync` MCP server (which runs NATIVELY, with reliable filesystem
    access) handle it the same way. Building via the MCP server sidesteps the
    sandbox bash mount that truncates large script-reads of plugin files."""
    if not Path(project).is_absolute():
        raise RuntimeError("project must be an ABSOLUTE path (got: %s)" % project)
    art, data_path, html_path = _paths(project, slug)
    art.mkdir(parents=True, exist_ok=True)
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding="utf-8"))
        if title:
            data["workspace"] = title
    else:
        data = _skeleton(title or (slug.replace("-", " ").title() + " Dashboard"))
        data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(_assemble(data), encoding="utf-8")
    return {"data": str(data_path), "html": str(html_path),
            "collections": len(data.get("collections", []))}


def cmd_build(a):
    try:
        print(json.dumps(build(a.project, a.slug, a.title)))
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
        s.add_argument("--slug", required=True)
        if name == "build":
            s.add_argument("--title", default=None)
    a = p.parse_args()
    {"build": cmd_build, "path": cmd_path}[a.cmd](a)


if __name__ == "__main__":
    main()
