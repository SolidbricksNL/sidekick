#!/usr/bin/env python3
"""Sidekick output-sync helper. Bidirectional file sync between a project's
local output/ and artifacts/ and an external base path (a mounted/synced
Drive/OneDrive folder): <base>/<project>/{output,artifacts}/. Plain file copies
(binary-safe) so a native run writes to the real filesystem the storage client
watches - no base64 through the model. Protocol: sync-discipline.md.
Keep this file small - Cowork truncates large plugin files on install."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

_CHUNK = 65536
_SUBDIRS = ("output", "artifacts")  # project subfolders kept in sync


def _die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _paths(project, base):
    # (project root, external base root <base>/<name>, manifest path, name).
    # Per subdir: local = proj/<sub>, remote = base_root/<sub>; manifest keys
    # are "<sub>/<relpath>".
    proj = Path(project)
    name = proj.name
    return proj, Path(base) / name, proj / ".sidekick-sync.json", name


def _walk(root):
    # Relative-path -> absolute Path for every regular file, dotfiles skipped.
    out = {}
    if not root.exists():
        return out
    for p in root.rglob("*"):
        if p.is_file() and not p.name.startswith(".") \
                and not any(part.startswith(".") for part in p.relative_to(root).parts):
            out[p.relative_to(root).as_posix()] = p
    return out


def _hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _load_manifest(p):
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("files", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _save_manifest(p, files):
    try:
        p.write_text(json.dumps({"version": 1, "files": files},
                                ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"warning: manifest not written ({e})", file=sys.stderr)


def reconcile(project, base_path, dry_run=False):
    """Two-way reconcile of <project>/{output,artifacts} <-> <base>/<name>/...
    Returns a summary dict. Raises RuntimeError if a side can't be read."""
    proj, base_root, mpath, name = _paths(project, base_path)
    warnings = []
    if not Path(project).is_absolute():
        warnings.append(f"project path {project!r} is relative; pass an absolute "
                        f"path to avoid resolving against the wrong directory")
    if not any((proj / s).exists() for s in _SUBDIRS):
        warnings.append(f"no {'/'.join(_SUBDIRS)} dir under {proj} - nothing local "
                        f"to push (is the project path correct/absolute?)")
    # Build maps keyed by "<sub>/<relpath>" across all synced subdirs.
    Lmap, Rmap = {}, {}
    for sub in _SUBDIRS:
        for rel, p in _walk(proj / sub).items():
            Lmap[f"{sub}/{rel}"] = p
        for rel, p in _walk(base_root / sub).items():
            Rmap[f"{sub}/{rel}"] = p
    base = _load_manifest(mpath)
    try:
        lh = {k: _hash(v) for k, v in Lmap.items()}
        rh = {k: _hash(v) for k, v in Rmap.items()}
    except OSError as e:
        raise RuntimeError(f"could not read files (storage path reachable?): {e}")
    do = not dry_run
    new, pushed, pulled, insync, conflicts, errors = {}, [], [], 0, [], []
    for k in sorted(set(lh) | set(rh) | set(base)):
        b, l, r = base.get(k), lh.get(k), rh.get(k)
        ldest, rdest = proj / k, base_root / k          # k = "<sub>/<relpath>"
        try:
            if l and r:
                if l == r:
                    new[k] = l
                    insync += 1
                elif b is not None and l == b:        # only remote changed -> pull
                    if do:
                        _copy(Rmap[k], ldest)
                    new[k] = r
                    pulled.append(k)
                elif b is not None and r == b:        # only local changed -> push
                    if do:
                        _copy(Lmap[k], rdest)
                    new[k] = l
                    pushed.append(k)
                else:                                 # both changed (or no baseline) -> conflict
                    conflicts.append(k)
                    if b is not None:
                        new[k] = b
            elif l and not r:                         # local only -> push (additive)
                if do:
                    _copy(Lmap[k], rdest)
                new[k] = l
                pushed.append(k)
            elif r and not l:                         # remote only -> pull (additive)
                if do:
                    _copy(Rmap[k], ldest)
                new[k] = r
                pulled.append(k)
            # else: only in baseline (gone both sides) -> drop from manifest
        except OSError as e:
            errors.append({"file": k, "error": str(e)})
    if do:
        _save_manifest(mpath, new)
    return {"ok": True, "action": "reconcile", "project": name,
            "base": str(base_root), "subdirs": list(_SUBDIRS), "dry_run": dry_run,
            "pushed": pushed, "pulled": pulled, "in_sync": insync,
            "conflicts": conflicts, "errors": errors, "warnings": warnings}


def cmd_reconcile(args):
    try:
        _emit(reconcile(args.project, args.base, args.dry_run))
    except RuntimeError as e:
        _die(f"error: {e}")


def resolve(project, base_path, file, keep):
    """Settle one conflict; file is a manifest key "<sub>/<relpath>". Returns a
    summary dict. Raises RuntimeError if the chosen side's file is missing."""
    proj, base_root, mpath, name = _paths(project, base_path)
    files = _load_manifest(mpath)
    k = file
    lp, rp = proj / k, base_root / k
    if keep == "local":
        if not lp.exists():
            raise RuntimeError(f"local file {k!r} not found")
        _copy(lp, rp)
        files[k] = _hash(lp)
    elif keep == "external":
        if not rp.exists():
            raise RuntimeError(f"external file {k!r} not found")
        _copy(rp, lp)
        files[k] = _hash(rp)
    elif keep == "both":
        if not rp.exists():
            raise RuntimeError(f"external file {k!r} not found")
        kp = Path(k)
        alt = kp.with_name(f"{kp.stem}.from-external{kp.suffix}").as_posix()
        _copy(rp, proj / alt)             # preserve external version under a new name
        _copy(proj / alt, base_root / alt)
        files[alt] = _hash(proj / alt)
        if lp.exists():                   # local keeps the original name on both sides
            _copy(lp, rp)
            files[k] = _hash(lp)
    _save_manifest(mpath, files)
    return {"ok": True, "action": "resolve", "project": name,
            "file": k, "keep": keep}


def cmd_resolve(args):
    try:
        _emit(resolve(args.project, args.base, args.file, args.keep))
    except RuntimeError as e:
        _die(f"error: {e}")


def build_parser():
    p = argparse.ArgumentParser(prog="sync.py",
                                description="Sidekick output-sync helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reconcile", help="two-way sync output/ <-> base; reports conflicts")
    r.add_argument("--project", required=True, help="path to the workspace project dir")
    r.add_argument("--base", required=True, help="external base path (mounted/synced folder)")
    r.add_argument("--dry-run", action="store_true", help="report planned actions, change nothing")
    r.set_defaults(func=cmd_reconcile)

    s = sub.add_parser("resolve", help="resolve one conflict from a reconcile")
    s.add_argument("--project", required=True)
    s.add_argument("--base", required=True)
    s.add_argument("--file", required=True, help="conflicting relative path under output/")
    s.add_argument("--keep", required=True, choices=["local", "external", "both"])
    s.set_defaults(func=cmd_resolve)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
