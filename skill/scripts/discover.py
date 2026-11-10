#!/usr/bin/env python3
"""跨平台发现 NL 工件，替代 /nlpm:ls 与 scanner agent。

用法：
  python scripts/discover.py <path> [--json]

覆盖 Claude Code / CodeBuddy / WorkBuddy / Codex / Antigravity 的路径。
输出：path, tier, kind, lines。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKIP = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
    "build", "target", "vendor", ".next", ".pytest_cache", "cache",
    "fixtures", "evals",
}


def classify(rel: Path) -> tuple[str, str] | None:
    parts = rel.parts
    name = rel.name
    posix = rel.as_posix()
    if name == ".gitkeep":
        return None

    if name == "SKILL.md":
        return "universal", "skill"
    if name in {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}:
        return "universal", "memory"
    if name == "plugin.json" and parts[0] in {
        ".claude-plugin", ".codebuddy-plugin", ".workbuddy-plugin", ".codex-plugin"
    }:
        tier = "workbuddy" if parts[0] in {".codebuddy-plugin", ".workbuddy-plugin"} else (
            "codex" if parts[0] == ".codex-plugin" else "claude"
        )
        return tier, "manifest"
    if name == "marketplace.json" and parts[0] in {
        ".claude-plugin", ".codebuddy-plugin", ".workbuddy-plugin"
    }:
        return "workbuddy" if parts[0] != ".claude-plugin" else "claude", "manifest"
    if posix.startswith("commands/") and rel.suffix == ".md":
        return "claude", "command"
    if posix.startswith("agents/") and rel.suffix == ".md":
        return "claude", "agent"
    if posix.startswith("hooks/") and rel.suffix == ".json":
        return "claude", "hook"
    if name in {"settings.json", "settings.local.json", "mcp.json", ".mcp.json", "hooks.json", "config.toml"}:
        if any(p in {".claude", ".codebuddy", ".workbuddy"} for p in parts) or posix.startswith("."):
            return "workbuddy" if any(p in {".codebuddy", ".workbuddy"} for p in parts) else "claude", "config"
        return "claude", "config"
    if posix.startswith(".claude/") and rel.suffix in {".md", ".json"}:
        return "claude", "project"
    if posix.startswith((".codebuddy/", ".workbuddy/")) and rel.suffix in {".md", ".json"}:
        return "workbuddy", "project"
    if posix.startswith((".codex/", ".agents/", ".codex-plugin/")) and rel.suffix in {".md", ".toml", ".json"}:
        return "codex", "project"
    if posix.startswith((".gemini/", ".agent/")) or name == "gemini-extension.json":
        return "antigravity", "project"
    if name in {".lsp.json"}:
        return "claude", "config"
    return None


def walk(root: Path):
    root = root.resolve()
    if root.is_file():
        yield root, Path(root.name)
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP for part in path.relative_to(root).parts):
            continue
        yield path, path.relative_to(root)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"路径不存在：{root}", file=sys.stderr)
        return 2

    found = []
    for path, rel in walk(root):
        hit = classify(rel)
        if not hit:
            continue
        try:
            lines = len(path.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            lines = 0
        found.append({
            "path": str(path),
            "tier": hit[0],
            "kind": hit[1],
            "lines": lines,
        })

    found.sort(key=lambda x: (x["tier"], x["kind"], x["path"]))
    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        print(f"{len(found)} 个 NL 工件 · 根目录 {root.resolve()}")
        by_tier: dict[str, int] = {}
        for f in found:
            by_tier[f["tier"]] = by_tier.get(f["tier"], 0) + 1
        print("  " + "  ".join(f"{k}={v}" for k, v in sorted(by_tier.items())))
        print()
        print(f"{'tier':<14}{'kind':<12}{'lines':>6}  path")
        for f in found[:40]:
            print(f"{f['tier']:<14}{f['kind']:<12}{f['lines']:>6}  {f['path']}")
        if len(found) > 40:
            print(f"... 其余 {len(found) - 40} 个用 --json 查看")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
