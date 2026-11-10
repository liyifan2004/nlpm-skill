#!/usr/bin/env python3
"""Pack skill/ into an installable zip, with the license notices.

Usage:
  python tools/pack.py [--out PATH] [--check]

The archive root is named after the skill's frontmatter `name`.
Both license texts and the notices travel inside the archive, so a skill
installed on its own still carries the upstream attribution.
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTICES = ["LICENSE", "LICENSE-UPSTREAM", "NOTICE", "UPSTREAM_PIN", "UPSTREAM_FILES.txt"]


def skill_name() -> str:
    text = (ROOT / "skill/SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^name:\s*(.+)$", text, re.M)
    if not m:
        raise SystemExit("SKILL.md has no name field")
    return m.group(1).strip()


def entries(name: str) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    skill_root = ROOT / "skill"
    for p in sorted(skill_root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        out.append((p, f"{name}/{p.relative_to(skill_root).as_posix()}"))
    for n in NOTICES:
        p = ROOT / n
        if not p.is_file():
            raise SystemExit(f"missing notice file: {n}")
        out.append((p, f"{name}/{n}"))
    return out


def required(name: str) -> set[str]:
    return {
        f"{name}/SKILL.md",
        f"{name}/LICENSE-UPSTREAM",
        f"{name}/NOTICE",
        f"{name}/references/NOTICE.md",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "nlpm-skill.zip"))
    ap.add_argument("--check", action="store_true", help="verify an existing archive")
    args = ap.parse_args()
    name = skill_name()
    zpath = Path(args.out)

    if args.check:
        if not zpath.is_file():
            raise SystemExit(f"archive not found: {zpath}")
        with zipfile.ZipFile(zpath) as z:
            names = set(z.namelist())
        missing = required(name) - names
        if missing:
            print("archive is missing required files:")
            for n in sorted(missing):
                print(f"  {n}")
            return 1
        print(f"archive ok: {len(names)} files, {zpath.stat().st_size} bytes")
        return 0

    zpath.parent.mkdir(parents=True, exist_ok=True)
    items = entries(name)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in items:
            z.write(src, arc)
    print(f"wrote {zpath} ({len(items)} files, {zpath.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
