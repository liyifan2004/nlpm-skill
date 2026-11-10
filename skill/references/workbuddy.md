# WorkBuddy 约定补充

上游 nlpm 给 Claude Code、Codex CLI、Antigravity 各建了一份 Tier 2 表，没有 WorkBuddy 这一档。本文件按 `analysis/multi-tool-design-2026-05.md` 的分层补上：Tier 1 通用地板（`conventions/SKILL.md`）不动，这里是 Tier 2-WorkBuddy。

## 用户级路径

| 工件 | 位置 |
|---|---|
| 技能 | `~/.workbuddy/skills/<name>/SKILL.md`，可带 `references/`、`scripts/`、`templates/` |
| MCP 配置 | `~/.workbuddy/mcp.json` |
| 全局设置 | `~/.workbuddy/settings.json`，含 `enabledPlugins`、`pluginConfigs`、`skillOverrides` |
| 插件与市场 | `~/.workbuddy/plugins/` 下的 `marketplaces/`、`cache/`、`known_marketplaces.json`、`installed_plugins.json`、`configured-plugins.json` |
| 记忆 | `~/.workbuddy/memory/MEMORY.md` |

## 项目级路径

| 工件 | 位置 |
|---|---|
| 项目技能 | `{workspace}/.workbuddy/skills/<name>/SKILL.md` |
| 工作日志 | `{workspace}/.workbuddy/memory/YYYY-MM-DD.md`、`MEMORY.md` |
| 通用说明 | `AGENTS.md`（项目根） |
| 项目设置 | `{workspace}/.codebuddy/settings.json` |

## 插件清单

manifest 目录三种命名都合法，见到任一种都算有清单：`.codebuddy-plugin/plugin.json`（优先）、`.workbuddy-plugin/plugin.json`、`.claude-plugin/plugin.json`。市场清单一同理。

组件在插件根目录：`commands/`、`agents/`、`skills/`、`hooks/hooks.json`、`.mcp.json`、`.lsp.json`、`settings.json`、`bin/`。`commands/shared/` 里的 md 是共享片段，带 `user-invocable: false`，不当命令统计。

`settings.json` 当前只有 `agent` 键会生效，`subagentStatusLine` 仅识别不加载。

## 规则适用性

上游 `scoring/SKILL.md` 按工件类型分了 Skills / Agents / Commands 等表，打分前先确认类型。另有几条规则写进了 Skills 通用表，实际只适用于 Claude Code 生态，审计 WorkBuddy skill 时按下面口径处理。口径写在这里，不要每次打分临时改。

| 上游规则 | 上游写法 | WorkBuddy 口径 | 理由 |
|---|---|---|---|
| R06 `<example>` 块 | user-invocable skill 缺块 -10；`user-invocable` 缺省视为可调用 | 不扣分 | 开放平台的 skill 规范只要求 frontmatter 的 name/description 与正文指令，没有 `<example>` 要求。本目录 skill 普遍不带该字段，会 100% 命中 |
| R01 mention/use | 词以字面 token 出现、且子句明确要求检测或替换该词时豁免；仅反引号不算 | 按上游原文逐行判 | 规则库里「Penalized terms: ...」是自身职责描述，`handle errors properly` 仍是使用 |
| R04 触发短语 | description 需 3 个以上具体动作短语 | 保留，中文按「用户会怎么问」判 | 触发质量影响模型能否选中 skill，跟生态无关 |
| R07 范围说明 | 有关联 skill 时缺范围说明 -3 | 只在同目录确有近似 skill 时扣 | 孤立 skill 没有可交叉引用的对象 |

`scripts/recalibrate.py` 的 workbuddy 口径只自动剔除 R06 的 `<example>` 行。R01 要逐行判断，findings 里只有汇总数，脚本把高命中文件列进待复核清单，不自动改分。R06 的「技术 skill 通篇无示例」是通用要求，保留。

## 评分要点

1. SKILL.md 按 Tier 1 通用地板打分，套 `scoring/SKILL.md` 的 skill 表。
2. manifest 缺字段时，先确认三种目录名都没找到，再报缺失。
3. hook 事件用 CodeBuddy 自己的表，不套 Claude 表。常用事件：SessionStart、UserPromptSubmit、PreToolUse、PostToolUse、TaskCreated、TaskCompleted、Stop、ConfigChange、FileChanged。hook 类型有 command、http、prompt、agent。
4. 状态文件写项目 `.workbuddy/` 下；见到 `.claude/nlpm-*.json` 说明用了上游默认路径，报告里标出来即可，不扣分。
5. 用户级 `~/.workbuddy/skills/` 没有 manifest，这是正常布局。`nlpm-check.py` 的清单一致性检查对它不适用，改用 `discover.py` 的结果判断覆盖是否完整。

## 上游没覆盖的能力

连接器（`connector-status`）、专家（`expert-history.json`）、资料库、自动化任务（`automation_update`）是 WorkBuddy 特有的扩展面，上游三档评分表都没有对应行。审计这些对象时只报事实，不套用 Claude 的扣分项。
