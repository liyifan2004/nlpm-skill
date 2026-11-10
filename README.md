# nlpm-skill

An independent [Agent Skill](https://agentskills.io) port of [xiaolai/nlpm](https://github.com/xiaolai/nlpm).

The question this project answers: can a Claude Code plugin that scores
natural-language artifacts be turned into one portable skill without losing
what it does? This repository holds the skill, the tools that keep it aligned
with upstream, and the tests that check the claim. [中文说明](README.zh-CN.md).

**Unofficial port.** Not affiliated with or endorsed by Xiaolai Li or the
nlpm project. See [NOTICE](NOTICE) and [ATTRIBUTION.md](ATTRIBUTION.md).

## What upstream does

nlpm treats markdown files that steer agents as programs to lint: SKILL.md,
AGENTS.md, commands, agents, hooks, manifests. It ships as a Claude Code
plugin with 12 slash commands, 8 subagents, 17 knowledge skills, a PostToolUse
hook, and a standalone Python validator.

## What is here

The 17 knowledge skills, the 100-point rubric and the validator are copied
from upstream. The harness-specific parts are replaced.

| Upstream | Here | Difference |
|---|---|---|
| 17 knowledge skills, scoring tables | `skill/references/` | none |
| `bin/nlpm-check` | `skill/scripts/nlpm-check.py` | none |
| 12 slash commands | one `SKILL.md` workflow | no `/nlpm:*` entry point |
| 8 subagents | four Python scripts + host model | mechanical checks become deterministic; parallelism depends on the host |
| PostToolUse hook | pre-commit / CI, or an optional host hook | no in-session reminder |
| trend state, config, reports | `history.py`, `templates/` | none |
| manifest, namespace, marketplace updates | optional thin host shell | no automatic updates |

The scoring output is preserved. The part that cannot be preserved lives in
the host runtime: slash-command entry points, in-session hooks, marketplace
versioning. [docs/design.md](docs/design.md) has the full mapping and explains
why one universal skill plus one thin host shell satisfies both portability
and the full experience.

## Install

```bash
git clone https://github.com/xiaolai/nlpm .cache/upstream
python tools/build.py --upstream .cache/upstream
python tools/pack.py
```

Import `dist/nlpm-skill.zip` through your host's skill importer, or copy
`skill/` into the host's skills directory as `nlpm-skill/`. Python 3.11+
and the standard library are the only requirements.

## Use

Ask the host to "score the skills in <path>" or "check manifest consistency".
`skill/SKILL.md` routes the request through five steps: set the scoring
profile, discover artifacts, run mechanical checks, apply the rubric, write a
report and a snapshot.

A host-specific scoring profile is part of the design. The shipped profile
(`references/workbuddy.md`) records which upstream rules are Claude Code
conventions and should not be applied to other hosts. `scripts/recalibrate.py`
recomputes existing findings under that profile.

## Layout

```
skill/       the installable skill
tools/       build from upstream, pack the zip
tests/       regression tests, standard library only
docs/        design decisions and host compatibility
UPSTREAM_PIN pinned upstream commit
```

## Status

Early. The skill works in WorkBuddy and in any host that reads Agent Skills.
The optional host shell is not built yet. See [CHANGELOG.md](CHANGELOG.md).

## License

Authored code: ISC, see `LICENSE`. Copied upstream content: ISC, see
`LICENSE-UPSTREAM`. Both license texts travel with every distributed copy.
