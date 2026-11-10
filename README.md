# nlpm-skill

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg?style=flat-square)](LICENSE)
[![CI](https://github.com/liyifan2004/nlpm-skill/actions/workflows/ci.yml/badge.svg?style=flat-square)](https://github.com/liyifan2004/nlpm-skill/actions/workflows/ci.yml)
[![Upstream: xiaolai/nlpm](https://img.shields.io/badge/Upstream-xiaolai%2Fnlpm-lightgrey.svg?style=flat-square)](https://github.com/xiaolai/nlpm)

Lint the markdown files that steer your agent — `SKILL.md`, `AGENTS.md`,
commands, hooks, manifests — on a 100-point rubric, from any host that reads
[Agent Skills](https://agentskills.io). No plugin, marketplace or hook setup
needed. [中文说明](README.zh-CN.md).

Unofficial port. Not affiliated with or endorsed by Xiaolai Li or the nlpm
project.

## Install

```bash
git clone https://github.com/xiaolai/nlpm .cache/upstream
python tools/build.py --upstream .cache/upstream
python tools/pack.py
```

Import `dist/nlpm-skill.zip` through your host's skill importer, or copy
`skill/` into the host's skills directory as `nlpm-skill/`. Requires Python
3.11+ and nothing outside the standard library.

To check the install without changing any files:

```bash
python skill/scripts/discover.py <skills-dir>
```

It prints the artifacts it found, grouped by host.

## Use

Say "score the skills in `<path>`" or "check manifest consistency" in a host
that loaded the skill. `skill/SKILL.md` routes the request through five steps:
set the scoring profile, discover artifacts, run mechanical checks, apply the
rubric, then write a report and a snapshot.

## What is preserved

The 17 knowledge skills, the 100-point rubric and the standalone validator
come from upstream unchanged. The harness-specific parts are replaced.

| Upstream | Here | Difference |
|---|---|---|
| 17 knowledge skills, scoring tables | `skill/references/` | none |
| `bin/nlpm-check` | `skill/scripts/nlpm-check.py` | none |
| 12 slash commands | one `SKILL.md` workflow | no `/nlpm:*` entry point |
| 8 subagents | four Python scripts + host model | mechanical checks become deterministic; parallelism depends on the host |
| PostToolUse hook | pre-commit / CI, or an optional host hook | no in-session reminder |
| trend state, config, reports | `history.py`, `templates/` | none |
| manifest, namespace, marketplace updates | optional thin host shell | no automatic updates |

[docs/design.md](docs/design.md) has the full mapping, the three-layer loss
boundary, and the reason one universal skill plus one thin host shell is the
structure that keeps both portability and the full host experience.
[docs/compatibility.md](docs/compatibility.md) lists what each host supports.

## Known limits

- The optional host shell is not built yet.
- `discover.py` classifies by path pattern, not by reading host specs.
- R01's mention-versus-use exclusion still needs a per-line review;
  `scripts/recalibrate.py` flags high-hit files instead of changing scores.

## Credits

An independent port of [xiaolai/nlpm](https://github.com/xiaolai/nlpm)
v1.4.3 by Xiaolai Li, ISC licensed. The rubric, scoring tables and validator
are copied with path changes only; the exact file list is in
[ATTRIBUTION.md](ATTRIBUTION.md) and [UPSTREAM_FILES.txt](UPSTREAM_FILES.txt).
The upstream author has not reviewed this port.

Maintained by [@liyifan2004](https://github.com/liyifan2004).

## License

ISC — [LICENSE](LICENSE) for authored code, [LICENSE-UPSTREAM](LICENSE-UPSTREAM)
for copied upstream content. Both texts ship inside every archive.
