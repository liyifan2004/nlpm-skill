# Changelog

## 0.2.0 — 2026-11-11

- Added `scripts/recalibrate.py`: recompute findings under a named scoring
  profile, report per-group averages and rank fixes by score recovered.
- Added the rule-applicability table in `references/workbuddy.md`. Upstream
  R06 requires `<example>` blocks on user-invocable skills; that is a Claude
  Code convention and inflated the loss on other hosts by 10 points per file.
- `SKILL.md` now fixes the scoring profile before any scoring starts, and
  keeps state files in the workspace instead of the scanned directory.
- Fixed R01 candidate handling: a backtick alone is not an exemption; the
  host applies the upstream mention-versus-use exclusion.

## 0.1.0 — 2026-11-10

- First portable skill port. Copied the 17 upstream knowledge skills, the
  scoring tables and `nlpm-check`; replaced commands, subagents and hooks
  with one workflow and four scripts.
- Added `discover.py`, `vague-scan.py`, `history.py`, and `build.py` for
  regenerating derived files from upstream.
- Verified against a 319-artifact corpus. The run showed that scoring output
  is reproducible and that the scoring profile has to be host-specific.
