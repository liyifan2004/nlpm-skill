#!/usr/bin/env python3
"""按规则口径重算分数，给出分组统计与修复收益排序。

用法：
  python scripts/recalibrate.py <findings.json> [--profile upstream|workbuddy]
        [--out scores.json] [--summary summary.json] [--drop RULE[:片段]]

profile=workbuddy 剔除 R06 的 <example> 块扣分。WorkBuddy 的 skill 规范只要求
frontmatter 的 name/description 和正文指令，没有 <example> 块要求；上游
scoring/SKILL.md 的 Skills 表把它写成通用规则，属于 Claude Code 生态惯例。

R01 的 mention-versus-use 排除需要逐行判断，findings 里只有汇总数，
本脚本不自动改 R01，只把高命中文件列进待复核清单。

--drop 可重复，格式 RULE 或 RULE:check 片段，用于自定义剔除。
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

BANDS = {"90+": (90, 101), "80-89": (80, 90), "70-79": (70, 80),
         "60-69": (60, 70), "<60": (0, 60)}


def drop_finding(f: dict, profile: str, drops: list[str]) -> bool:
    rule = f.get("rule", "")
    check = f.get("check", "")
    if profile == "workbuddy" and rule == "R06" and "<example>" in check:
        return True
    for spec in drops:
        r, _, frag = spec.partition(":")
        if rule == r and (not frag or frag in check):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("findings")
    ap.add_argument("--profile", choices=["upstream", "workbuddy"], default="workbuddy")
    ap.add_argument("--out", default="")
    ap.add_argument("--summary", default="")
    ap.add_argument("--drop", action="append", default=[])
    args = ap.parse_args()

    src = Path(args.findings)
    if not src.is_file():
        print(f"找不到 {src}", file=sys.stderr)
        return 2
    rows = json.loads(src.read_text(encoding="utf-8"))
    base = src.parent
    out = Path(args.out) if args.out else base / "nlpm-scores-calibrated.json"
    summary_path = Path(args.summary) if args.summary else base / "nlpm-summary-calibrated.json"

    scores: dict[str, int] = {}
    gains: dict[str, dict] = {}
    r01_review: list[str] = []
    dropped = 0

    for x in rows:
        kept_loss = 0
        for f in x["findings"]:
            if drop_finding(f, args.profile, args.drop):
                dropped += 1
                continue
            loss = abs(f.get("penalty", 0))
            kept_loss += loss
            key = f"{f.get('rule', '--')}|{f.get('check', '')[:24]}"
            g = gains.setdefault(key, {"files": 0, "loss": 0, "rule": f.get("rule", "--")})
            g["files"] += 1
            g["loss"] += loss
            if f.get("rule") == "R01" and loss >= 10:
                r01_review.append(x["path"])
        scores[x["path"]] = max(0, 100 - kept_loss)

    groups: dict[str, list[int]] = collections.defaultdict(list)
    for x in rows:
        groups[x.get("group", "other")].append(scores[x["path"]])
    vals = list(scores.values())

    summary = {
        "profile": args.profile,
        "files": len(rows),
        "avg_all": round(statistics.mean(vals), 1),
        "dropped_findings": dropped,
        "group_avg": {k: round(statistics.mean(v), 1) for k, v in sorted(groups.items())},
        "group_count": {k: len(v) for k, v in sorted(groups.items())},
        "bands": {k: sum(1 for v in vals if lo <= v < hi) for k, (lo, hi) in BANDS.items()},
        "below_70": sum(1 for v in vals if v < 70),
        "fix_priority": [
            {"check": k, "rule": g["rule"], "files": g["files"],
             "loss": g["loss"], "avg_gain_if_fixed": round(g["loss"] / len(rows), 2)}
            for k, g in sorted(gains.items(), key=lambda kv: -kv[1]["loss"])[:12]
        ],
        "r01_review_needed": sorted(set(r01_review)),
        "worst": [{"path": p, "score": s} for p, s in sorted(scores.items(), key=lambda kv: kv[1])[:15]],
    }

    out.write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"profile={args.profile} · 剔除 {dropped} 条不适用扣分 · 均分 {summary['avg_all']}")
    print("分组：" + "  ".join(f"{k}={v}({summary['group_count'][k]})" for k, v in summary["group_avg"].items()))
    print(f"低于 70：{summary['below_70']} 个 · 待复核 R01：{len(summary['r01_review_needed'])} 个文件")
    print("修复收益前 5：")
    for g in summary["fix_priority"][:5]:
        print(f"  {g['rule']:<5} {g['check'][:34]:<36} {g['files']:>3} 文件  累计 -{g['loss']}")
    print(f"写出 {out.name} 与 {summary_path.name}")
    return 0


if __name__ == "__main__":
    # Windows consoles default to cp1252; keep the CLI output UTF-8.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
