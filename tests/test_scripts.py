"""Regression tests. Run: python -m unittest discover -s tests -v"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "scripts"


def load(module_name: str, filename: str):
    path = SCRIPTS / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class DiscoverTests(unittest.TestCase):
    def setUp(self):
        self.m = load("discover", "discover.py")

    def test_classifies_common_paths(self):
        cases = {
            "foo/SKILL.md": ("universal", "skill"),
            "AGENTS.md": ("universal", "memory"),
            ".claude-plugin/plugin.json": ("claude", "manifest"),
            ".codebuddy-plugin/plugin.json": ("workbuddy", "manifest"),
            ".workbuddy-plugin/marketplace.json": ("workbuddy", "manifest"),
            ".codex-plugin/plugin.json": ("codex", "manifest"),
            "commands/score.md": ("claude", "command"),
            "agents/scorer.md": ("claude", "agent"),
            "hooks/hooks.json": ("claude", "hook"),
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(self.m.classify(Path(path)), expected)

    def test_skips_gitkeep(self):
        self.assertIsNone(self.m.classify(Path(".gemini/skills/.gitkeep")))

    def test_walk_skips_fixtures(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "evals").mkdir()
            (root / "evals/a.md").write_text("x", encoding="utf-8")
            (root / "b.md").write_text("y", encoding="utf-8")
            found = [str(rel) for _, rel in self.m.walk(root)]
            self.assertIn("b.md", found)
            self.assertFalse(any("evals" in f for f in found))


class VagueScanTests(unittest.TestCase):
    def setUp(self):
        self.m = load("vague_scan", "vague-scan.py")

    def test_counts_and_marks_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.md"
            p.write_text(
                "Use appropriate values.\n"
                "Set several retries.\n"
                "This is relevant to the SLO target of 99.9% uptime.\n"
                "Pick various options.\n",
                encoding="utf-8",
            )
            r = self.m.scan(p)
        self.assertEqual(r["count"], 3)
        self.assertEqual(r["candidate_count"], 1)
        self.assertEqual(r["penalty"], -6)

    def test_backticked_terms_are_candidates(self):
        self.assertTrue(self.m.in_code("Flag `some` and `several`", 8))


class HistoryTests(unittest.TestCase):
    script = str(SCRIPTS / "history.py")

    def test_duplicate_snapshot_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            scores = root / "scores.json"
            scores.write_text(json.dumps({"a/SKILL.md": 82}), encoding="utf-8")
            state = root / "history.json"
            for _ in range(2):
                r = subprocess.run(
                    [sys.executable, self.script, "append", "--state", str(state),
                     "--scope", "full", "--scores", str(scores)],
                    capture_output=True, text=True,
                )
                self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(len(data), 1)


class RecalibrateTests(unittest.TestCase):
    script = str(SCRIPTS / "recalibrate.py")

    def _findings(self, path: Path):
        rows = [{
            "path": "a/SKILL.md", "group": "top", "kind": "skill", "lines": 10,
            "score": 85, "r01": {}, "vague_scan_candidates": 0,
            "findings": [
                {"rule": "R06", "check": "no <example> block", "penalty": -10},
                {"rule": "R04", "check": "trigger words missing", "penalty": -5},
            ],
        }]
        path.write_text(json.dumps(rows), encoding="utf-8")

    def test_upstream_profile_reproduces_scores(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            f = root / "findings.json"
            self._findings(f)
            r = subprocess.run(
                [sys.executable, self.script, str(f), "--profile", "upstream"],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            scores = json.loads((root / "nlpm-scores-calibrated.json").read_text(encoding="utf-8"))
            self.assertEqual(scores["a/SKILL.md"], 85)

    def test_workbuddy_profile_drops_example_rule(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            f = root / "findings.json"
            self._findings(f)
            r = subprocess.run(
                [sys.executable, self.script, str(f), "--profile", "workbuddy"],
                capture_output=True, text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            scores = json.loads((root / "nlpm-scores-calibrated.json").read_text(encoding="utf-8"))
            self.assertEqual(scores["a/SKILL.md"], 95)


class PackageTests(unittest.TestCase):
    def test_build_check_when_upstream_present(self):
        up = ROOT / ".cache" / "upstream"
        if not (up / "skills" / "nlpm").is_dir():
            self.skipTest("upstream checkout not present")
        r = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build.py"), "--check", "--upstream", str(up)],
            capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_package_contains_notices(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "skill.zip"
            for args in ([], ["--check"]):
                r = subprocess.run(
                    [sys.executable, str(ROOT / "tools" / "pack.py"), "--out", str(out)] + args,
                    capture_output=True, text=True,
                )
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
