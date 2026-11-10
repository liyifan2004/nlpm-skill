# Upstream tracking

- Repository: https://github.com/xiaolai/nlpm
- Pinned commit: `UPSTREAM_PIN` (one SHA, plain text)
- Upstream version at pin: 1.4.3
- Relationship: independent port, not a GitHub fork

A port shares almost no tree with the plugin. Upstream carries 1800+ files of
auditor reports, workflows and generated data; this project ships one skill.
A fork would carry that unrelated history and be permanently labelled a fork
even though no change is expected to flow back. Attribution lives in README,
NOTICE, ATTRIBUTION.md, CITATION.cff and inside the shipped skill instead.

## Sync procedure

1. Clone upstream into `.cache/upstream` and check out the commit in `UPSTREAM_PIN`.
2. Run `python tools/build.py --upstream .cache/upstream`.
3. Run `python -m unittest discover -s tests -v`.
4. Review the diff under `skill/references/` and `skill/scripts/nlpm-check.py`.
5. Update `UPSTREAM_PIN`, `CHANGELOG.md` and the version in `skill/SKILL.md`.

CI runs `tools/build.py --check` against the pinned commit and fails when a
generated file was edited by hand.

Files copied from upstream are generated. Do not edit them here. A rule change
belongs in an upstream issue or pull request.
