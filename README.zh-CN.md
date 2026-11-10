# nlpm-skill 中文说明

把 [xiaolai/nlpm](https://github.com/xiaolai/nlpm) 的规则层抽成一个通用
Agent Skill。项目要回答的问题只有一个：一个给 Claude Code 做的插件，能不能
变成一个跨宿主可用的 skill，且打分、检查、修复这些产出不打折。

这是非官方移植，与原作者和上游项目没有隶属或背书关系。归属声明见
`NOTICE`、`ATTRIBUTION.md`，许可原文见 `LICENSE`、`LICENSE-UPSTREAM`。

## 保留了什么

上游的 17 份知识 skill、100 分评分表、50 条规则、纯标准库的
`nlpm-check` 原样搬进 `skill/references/` 和 `skill/scripts/`。12 个斜杠
命令收进一个 `SKILL.md` 工作流；8 个子代理里机械的部分写成四个脚本，
判断的部分交给宿主模型；趋势、配置、报告由 `history.py` 和模板接住。

## 折损在哪里

折损集中在宿主机制，不在内容：斜杠命令的 `/nlpm:*` 入口、写完文件后在
会话里自动提醒的 hook、插件市场的版本自动更新。前两样可以用薄命令壳和
pre-commit / CI 补上，第三样需要宿主支持。详细映射和双层结构见
`docs/design.md`。

## 安装与使用

```bash
git clone https://github.com/xiaolai/nlpm .cache/upstream
python tools/build.py --upstream .cache/upstream
python tools/pack.py
```

把 `dist/nlpm-skill.zip` 通过宿主的技能导入功能安装，或把 `skill/`
复制成宿主 skills 目录下的 `nlpm-skill/`。之后在对话里说「给某个目录
的 skill 打分」即可。需要 Python 3.11+，无第三方依赖。

## 口径校准

上游评分表里有几条 Claude Code 生态惯例被写成了通用规则。例如 R06 要求
user-invocable skill 必须带 `<example>` 块，而多数宿主没有这个要求，
照搬会让几乎每个文件白扣 10 分。`skill/references/workbuddy.md` 记了
适用性口径，`skill/scripts/recalibrate.py` 按口径重算分数并给出修复收益
排序。打分测试是验证手段，项目目标仍是开头那个问题。
