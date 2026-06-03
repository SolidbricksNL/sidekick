#!/usr/bin/env python3
"""Build a self-contained Sidekick dashboard HTML from a small SK-data JSON.

The agent NEVER reads or pastes the ~11 KB UI kernel — this script reads
assets/ui.css + ui.js + solidbricks.png from disk (full, native, no context
truncation) and bakes the complete page. The only thing the agent edits per
dashboard is the tiny  artifacts/<slug>-dashboard.sk.json  data file.

Why a script: pasting the kernel inline made Cowork's agent-read truncate it
(~11.4 KB), producing blank dashboards. A native read sidesteps that entirely.

Layout (one dashboard per project; new one only on explicit request):
  <project>/artifacts/<slug>-dashboard.sk.json   <- source of truth (agent edits)
  <project>/artifacts/<slug>-dashboard.html      <- built output (synced to Drive)

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


def _assemble(data):
    css = (ASSETS / "ui.css").read_text(encoding="utf-8")
    js = (ASSETS / "ui.js").read_text(encoding="utf-8")
    # Truncation guard. A bad copy / install can cut an asset; baking a partial
    # kernel renders a BLANK page. Verify the end-sentinels and abort loudly with
    # the size instead of writing a broken dashboard. (The kernel must end with the
    # `render();` call; ui.css with a closing brace.)
    if not js.rstrip().endswith("render();"):
        sys.exit("ERROR: ui.js looks truncated (%d B; must end with 'render();'). "
                 "Reinstall the plugin — the dashboard was NOT written."
                 % len(js.encode("utf-8")))
    if len(css) < 4000 or not css.rstrip().endswith("}"):
        sys.exit("ERROR: ui.css looks truncated (%d B). Reinstall the plugin — "
                 "the dashboard was NOT written." % len(css.encode("utf-8")))
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
    art = Path(project) / "artifacts"
    return art, art / (slug + "-dashboard.sk.json"), art / (slug + "-dashboard.html")


def cmd_build(a):
    if not Path(a.project).is_absolute():
        sys.exit("ERROR: --project must be an ABSOLUTE path (got: %s)" % a.project)
    art, data_path, html_path = _paths(a.project, a.slug)
    art.mkdir(parents=True, exist_ok=True)
    if data_path.exists():
        data = json.loads(data_path.read_text(encoding="utf-8"))
        if a.title:
            data["workspace"] = a.title
    else:
        data = _skeleton(a.title or (a.slug.replace("-", " ").title() + " Dashboard"))
        data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(_assemble(data), encoding="utf-8")
    print(json.dumps({
        "data": str(data_path), "html": str(html_path),
        "collections": len(data.get("collections", [])),
        "created_skeleton": not a.title and not html_path.exists(),
    }))


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
