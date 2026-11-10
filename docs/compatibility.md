# Host compatibility

The skill itself follows the open Agent Skills format: one `SKILL.md` with
`name` and `description` frontmatter, plus `references/`, `scripts/` and
`templates/`. Anything that reads that format can load it. What differs is
the optional host shell.

| Host | Skill discovery | Slash commands | Event hooks | Subagents | Shell status |
|---|---|---|---|---|---|
| WorkBuddy / CodeBuddy | `~/.workbuddy/skills/<name>/SKILL.md`, project `.workbuddy/skills/` | `/<plugin>:<command>` | `hooks/hooks.json`, PostToolUse and more | yes | not built |
| Claude Code | `~/.claude/skills/`, plugin `skills/` | `/<plugin>:<command>` | PostToolUse and more | yes | not built |
| Codex CLI | `.agents/skills/` | no equivalent | `config.toml` hooks | TOML agent defs | not built |
| Antigravity / Gemini CLI | `.agent/skills/`, `.gemini/skills/` | TOML commands | own event table | own agent defs | not built |
| Generic Agent Skills host | whatever the host reads | none | none | optional | skill works as-is |

## Path notes

WorkBuddy accepts three manifest directory names: `.codebuddy-plugin/`,
`.workbuddy-plugin/` and `.claude-plugin/`. Its marketplace file can live in
any of them. `discover.py` knows all three plus the Codex and Antigravity
paths. `references/workbuddy.md` has the full table.

The upstream `nlpm-check` only looks for `.claude-plugin/plugin.json`. On a
bare skills directory it reports nothing. `discover.py` covers that case
instead; the manifest check stays limited to repositories that actually have
a manifest.

## Environment variables

The upstream plugin uses `${CLAUDE_PLUGIN_ROOT}` in 90 files. CodeBuddy
accepts that name too, but a portable skill cannot rely on any host variable.
This project uses paths relative to the skill directory and has no
PLUGIN_ROOT references.
