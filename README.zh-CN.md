# nlpm-skill 中文说明

[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg?style=flat-square)](LICENSE)
[![CI](https://github.com/liyifan2004/nlpm-skill/actions/workflows/ci.yml/badge.svg?style=flat-square)](https://github.com/liyifan2004/nlpm-skill/actions/workflows/ci.yml)
[![Upstream: xiaolai/nlpm](https://img.shields.io/badge/Upstream-xiaolai%2Fnlpm-lightgrey.svg?style=flat-square)](https://github.com/xiaolai/nlpm)

在任何支持 [Agent Skills](https://agentskills.io) 的宿主里，给 `SKILL.md`、
`AGENTS.md`、命令、hook、清单这类自然语言工件按 100 分制打分。不需要装
Claude Code 插件、加市场或配 hook。[English](README.md)

这是非官方移植，与原作者及上游项目没有隶属或背书关系。

## 安装

```bash
git clone https://github.com/xiaolai/nlpm .cache/upstream
python tools/build.py --upstream .cache/upstream
python tools/pack.py
```

用宿主的技能导入功能安装 `dist/nlpm-skill.zip`，或把 `skill/` 复制成宿主
skills 目录下的 `nlpm-skill/`。需要 Python 3.11+，无第三方依赖。

不改任何文件地验证安装：

```bash
python skill/scripts/discover.py <skills-dir>
```

会按宿主分组打印找到的工件。

## 使用

在已加载该 skill 的宿主里说「给 `<path>` 里的 skill 打分」或「检查清单一致性」。
`skill/SKILL.md` 把请求路由到五步：定评分口径、发现工件、跑机械检查、
套评分表、写报告和快照。

## 保留与折损

上游的 17 份知识 skill、100 分评分表和独立校验器原样保留；宿主相关的部分被替换。
完整映射、三层折损边界和双层结构见 [docs/design.md](docs/design.md)，
各宿主支持情况见 [docs/compatibility.md](docs/compatibility.md)。

内容层零折损。折损都在宿主机制：斜杠命令入口、会话内自动提醒、市场版本更新。
前两样可用薄命令壳和 pre-commit / CI 补上，第三样需要宿主支持。

## 已知限制

- 可选的宿主薄壳还没做。
- `discover.py` 按路径模式分类，不读宿主规范。
- R01 的 mention/use 排除仍需逐行判断；`scripts/recalibrate.py` 只标记高命中文件，不改分。

## 致谢

独立移植自 [xiaolai/nlpm](https://github.com/xiaolai/nlpm) v1.4.3，作者
Xiaolai Li，ISC 许可。评分表与校验器只改了路径，清单见
[ATTRIBUTION.md](ATTRIBUTION.md) 和 [UPSTREAM_FILES.txt](UPSTREAM_FILES.txt)。
上游作者未审阅本项目。

维护者 [@liyifan2004](https://github.com/liyifan2004)。

## 许可

ISC — 自写部分见 [LICENSE](LICENSE)，上游内容见
[LICENSE-UPSTREAM](LICENSE-UPSTREAM)。两份许可文本随每个压缩包分发。
