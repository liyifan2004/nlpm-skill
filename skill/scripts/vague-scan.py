#!/usr/bin/env python3
"""机械统计模糊量词，替代 vague-scanner agent。

用法：
  python scripts/vague-scan.py <file-or-dir> [--json]

词条来自 references/conventions/SKILL.md。逐词 -2，单文件上限 -20。
脚本只做机械计数：同行尾部带数字、冒号或度量词的一律标为候选，不替模型判断。
候选由宿主按 references/conventions/SKILL.md 的 R01 carve-out 逐条复核后再定扣分。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TERMS = [
    "appropriate", "relevant", "as needed", "sufficient", "adequate",
    "reasonable", "properly", "correctly", "some", "several", "various",
]
MEASURABLE = re.compile(r"\d|%|:|<=|>=|\bSLO\b|\bms\b|\bseconds?\b", re.I)
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def in_code(line: str, pos: int) -> bool:
    return line[:pos].count("`") % 2 == 1


def scan(path: Path) -> dict:
    hits: list[dict] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for term in TERMS:
            for m in re.finditer(r"\b" + re.escape(term) + r"\b", line, re.I):
                tail = line[m.end():m.end() + 60]
                hits.append({
                    "line": lineno,
                    "term": term,
                    "text": line.strip()[:120],
                    "candidate": bool(MEASURABLE.search(tail)) or in_code(line, m.start()),
                })
    effective = [h for h in hits if not h["candidate"]]
    penalty = max(-20, -2 * len(effective))
    return {
        "path": str(path),
        "hits": hits,
        "count": len(effective),
        "candidate_count": len(hits) - len(effective),
        "penalty": penalty,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"路径不存在：{target}", file=sys.stderr)
        return 2

    files: list[Path] = []
    if target.is_file():
        files = [target]
    else:
        for p in target.rglob("*.md"):
            if not any(part in SKIP for part in p.relative_to(target).parts):
                files.append(p)

    results = [scan(p) for p in sorted(files)]
    results = [r for r in results if r["count"] or r["candidate_count"]]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        total = sum(r["count"] for r in results)
        print(f"{len(files)} 个文件 · {len(results)} 个有命中 · 共 {total} 处")
        for r in results[:20]:
            print(f"  {r['path']}  {r['count']} 处计分 + {r['candidate_count']} 处待核  penalty {r['penalty']}")
            for h in r["hits"][:3]:
                flag = "待核" if h["candidate"] else "计分"
                print(f"    L{h['line']} [{h['term']}][{flag}] {h['text']}")
        if len(results) > 20:
            print(f"... 其余 {len(results) - 20} 个用 --json 查看")
    return 0


if __name__ == "__main__":
    # Windows consoles default to cp1252; keep the CLI output UTF-8.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
