#!/usr/bin/env python3
"""评分快照与趋势，替代 /nlpm:trend 的状态文件。

用法：
  python scripts/history.py append --state <file.json> --scope full --scores scores.json
  python scripts/history.py show  --state <file.json>

scores.json 格式：{"path/to/SKILL.md": 87, "AGENTS.md": 92}
状态文件放目标项目，不写进 skill 包。
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("append")
    a.add_argument("--state", required=True)
    a.add_argument("--scope", default="full")
    a.add_argument("--scores", required=True)
    s = sub.add_parser("show")
    s.add_argument("--state", required=True)
    args = ap.parse_args()

    state = Path(args.state)
    history = load(state)

    if args.cmd == "append":
        scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "scope": args.scope,
            "files": scores,
            "files_scored": len(scores),
            "avg": round(sum(scores.values()) / len(scores), 1) if scores else 0,
        }
        if history and history[-1].get("files") == scores and history[-1].get("scope") == args.scope:
            print("与上次快照相同，跳过写入")
            return 0
        history.append(entry)
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"写入快照 {entry['ts']} · {entry['files_scored']} 个文件 · 均分 {entry['avg']}")
        return 0

    if not history:
        print("没有历史快照，先跑一次评分")
        return 0
    print(f"{len(history)} 次快照 · 状态文件 {state}")
    prev = None
    for e in history:
        delta = "" if prev is None else f"  ({e['avg'] - prev:+.1f})"
        print(f"  {e['ts']}  {e['scope']:<12} {e['files_scored']:>4} 个  均分 {e['avg']:>5}{delta}")
        prev = e["avg"]
    return 0


if __name__ == "__main__":
    # Windows consoles default to cp1252; keep the CLI output UTF-8.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
