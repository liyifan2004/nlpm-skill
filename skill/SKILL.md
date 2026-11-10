---
name: nlpm-skill
description: 审计自然语言工件的质量（SKILL.md、AGENTS.md、commands、agents、hooks、配置），按 100 分制扣分，检查清单与磁盘一致性，修复可自动修的字段，记录均分趋势。用户说「给这些 skill 打分」「检查插件清单」「lint 一下提示词」「规则有没有跑偏」时使用。跨宿主可用，不依赖 Claude Code。
version: 0.1.0
---

# nlpm universal

一套规则，任何支持 Agent Skills 的宿主都能跑。规则、评分表、写作指南来自 xiaolai/nlpm v1.4.3；命令编排、子代理分工、hook 提醒换成了脚本和明确的步骤。

## 开始前

把本 skill 所在目录记为 ROOT。脚本用 `python ROOT/scripts/<name>.py` 调用。状态文件写在工作区，不要写进 ROOT，也不要写进被扫描的 skills 目录。

## 打分前先定口径

口径先定下来再算分，否则全量分数会一起偏低，后面的优先级全错。

1. 按工件类型取表。`references/scoring/SKILL.md` 按类型分了 Skills / Agents / Commands / Hooks / plugin.json 等表，只对当前类型应用对应的行。
2. 查 `references/workbuddy.md` 的「规则适用性」。上游把几条 Claude Code 生态惯例写进了通用表，里面列了处理办法。
3. 分开统计。已装 skill、第三方集合里的嵌套 skill、工具自带的规则文档各算各的均分，不混成一个数。

拿已有 findings 重算时跑 `python ROOT/scripts/recalibrate.py <findings.json> --profile workbuddy`，看它输出的分组均分和修复收益排序。

## 用户要什么，跑什么

- 列出工件 → 第 1 步
- 打分 → 第 1 到 4 步
- 检查清单一致性 → 第 1 步后跑 `scripts/nlpm-check.py`
- 修复 → 第 3 步拿到 finding 后，只改可自动修的字段
- 看趋势 → 第 5 步
- 安全扫描 → 读 `references/security/SKILL.md`
- 写测试规格 → 读 `references/testing/SKILL.md`

## 步骤

1. 发现。跑 `python ROOT/scripts/discover.py <目标路径> --json`，输出每个工件的 path / tier / kind / lines。按 tier 选约定：universal 读 `references/conventions/SKILL.md`，claude 读 `references/conventions-claude/SKILL.md`，codex 读 `references/conventions-codex/SKILL.md`，antigravity 读 `references/conventions-antigravity/SKILL.md`，workbuddy 读 `references/workbuddy.md`。
2. 机械扫描。跑 `python ROOT/scripts/vague-scan.py <目标路径> --json`，逐词统计模糊量词，每处 -2，单文件最多 -20。脚本把带度量线索或反引号内的命中标为候选；按 `references/scoring/SKILL.md` 的 mention-versus-use exclusion 和 `references/conventions/SKILL.md` 的 R01 carve-out 逐条复核后再定扣分，反引号本身不算豁免理由。宿主有子代理就按文件分批委派，一批最多 5 个；没有就顺序跑，结果一样。
3. 判断打分。读 `references/scoring/SKILL.md` 和 `references/rules/SKILL.md`，按表格从 100 分往下扣。附表索引在 `references/INDEX.md`，分数落在 58-62、68-72、88-92 这几段时读 `references/scoring/references/calibration-examples.md`。只报表里列过的扣分项。每个 finding 写清 severity、规则号、行号、扣分、改法。
4. 结构化检查。跑 `python ROOT/scripts/nlpm-check.py <目标路径> --json`。它只覆盖带 manifest 的插件仓库，查 SKILL.md 在磁盘上却没写进 plugin.json 这类问题。
5. 报告与快照。给出每文件分数、finding 列表、分组均分。把分数写成 JSON，跑 `python ROOT/scripts/history.py append --state <工作区>/.nlpm-history.json --scope full --scores <scores.json>`；用 `show` 看趋势。报告里附一条修复收益排序，按「修好这一类能提多少分、覆盖多少文件」排，别按文件数排。

## 配置

被审计项目可放 `.nlpm.local.md`，声明 `strictness`（relaxed / standard / strict）、`score_threshold`（默认 70）、`rule_overrides`。没有就用默认值。

## 宿主差异

- 有子代理：第 2、3 步按文件分批委派。
- 有事件 hook：在 PostToolUse 调 `scripts/nlpm-check.py` 做提醒。没有就把同一条命令放进 pre-commit 或 CI，写入文件后仍会检查。
- 有斜杠命令：可加一层薄命令壳转发到上面的步骤。壳子可有可无，能力都在本文件里。
- 路径一律相对，不用任何宿主的 PLUGIN_ROOT 变量。

## 不做什么

不追 100 分，85 以上够用。不发明评分表以外的扣分项。不手改上游派生文件，它们由 `ROOT/build.py` 重新生成。
