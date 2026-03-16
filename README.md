# Skills Master

`skills-master` 是一个面向多 Agent / 多工具环境的 skills 工程工具包。

它现在的主定位不是“某个平台遗留的 skill 样板”，而是一个完整的 skills 维护仓库，用来处理这些事情：

1. 新建 skill
2. 重写已经过拟合或膨胀的 skill
3. 设计评测集、对比基线和人工复核流程
4. 优化 skill 的触发描述与元数据
5. 维护一套 skills 在不同工具目录下的真实源与链接关系

## 当前定位

本仓库已经按下面的边界重新整理：

- 主叙事改为“通用 skills 工程”，不再把继承自 Claude 的历史措辞当成默认前提。
- 通用方法与平台特定能力分开描述。
- `README.md` 只负责仓库入口、边界和使用方式。
- `SKILL.md` 只负责这个 skill 本身的工作流与执行原则。
- 仍然保留必要的兼容信息，但不再让旧平台假设主导全文。

## 能力分层

### 通用且稳定

这些能力不依赖单一平台，属于本项目的主路径：

- 设计或重写 `SKILL.md`
- 组织 `scripts/`、`references/`、`assets/`
- 初始化 skill 目录
- 基础结构校验
- 评测结果归档与 benchmark 聚合
- 多工具目录的软链接管理
- `.skill` 打包

### 平台相关

这些能力目前仍绑定特定运行环境，文档里会明确标注：

- `scripts/run_eval.py`
- `scripts/run_loop.py`
- `scripts/improve_description.py`

上面这组脚本依赖 Anthropic SDK 与 `claude` CLI，用于描述触发优化和触发率评测。它们是可选增强能力，不是整个项目的默认前提。

## 仓库结构

```text
skills-master/
├── SKILL.md
├── README.md
├── VERSION.md
├── LICENSE.txt
├── agents/
│   ├── analyzer.md
│   ├── comparator.md
│   └── grader.md
├── assets/
│   └── eval_review.html
├── eval-viewer/
│   ├── generate_review.py
│   └── viewer.html
├── references/
│   ├── output-patterns.md
│   ├── schemas.md
│   └── workflows.md
└── scripts/
    ├── aggregate_benchmark.py
    ├── generate_report.py
    ├── improve_description.py
    ├── init_skill.py
    ├── link_skill.py
    ├── package_skill.py
    ├── quick_validate.py
    ├── run_eval.py
    ├── run_loop.py
    └── utils.py
```

## 文档分工

- `README.md`: 仓库入口、能力边界、快速上手、依赖说明
- `SKILL.md`: 这个 skill 的执行说明，面向真正调用 skill 的 agent
- `VERSION.md`: 当前版本定位与变更方向
- `references/`: 写 skill 时按需读取的结构化参考
- `agents/`: 评测、对比、分析等辅助角色说明

## 快速使用

### 1. 初始化一个新 skill

```bash
python3 scripts/init_skill.py my-skill --path ~/.agents/skills
```

### 2. 校验 skill 结构

```bash
python3 -m scripts.quick_validate /path/to/my-skill
```

### 3. 检查或创建链接

```bash
python3 scripts/link_skill.py /path/to/my-skill --status
python3 scripts/link_skill.py /path/to/my-skill
```

### 4. 打包为 `.skill`

```bash
python3 -m scripts.package_skill /path/to/my-skill
```

### 5. 聚合 benchmark

```bash
python3 -m scripts.aggregate_benchmark /path/to/workspace/iteration-1 --skill-name my-skill
```

## 触发描述优化

如果你明确要做“trigger / description optimization”，再使用下面这组脚本：

```bash
python3 -m scripts.run_eval --help
python3 -m scripts.run_loop --help
```

使用前请确认：

1. 已安装 `anthropic`
2. 当前环境可用 `claude` CLI
3. 你接受这部分流程是 Anthropic / Claude 专用能力，而不是工具无关能力

## 真实源与链接策略

推荐把 skill 的唯一可编辑真源放在下面两个位置之一：

- 用户级：`~/.agents/skills/<skill-name>`
- 项目级：`<project-root>/.agents/skills/<skill-name>`

然后通过 `link_skill.py` 映射到工具侧目录，而不是在每个工具目录里维护一份独立副本。

当前脚本支持的目标包括：

- Claude Code: `.claude/skills` 或 `~/.claude/skills`
- Codex: `.codex/skills` 或 `~/.codex/skills`
- Antigravity: `~/.gemini/antigravity/skills`，项目级默认直接使用 `.agents/skills`

## 当前已知边界

- 仓库里还没有统一的 `requirements.txt` / `pyproject.toml`。
- 部分脚本需要以 `python3 -m scripts.<name>` 方式调用更稳妥，尤其是存在包内导入时。
- 触发评测链路当前仍然围绕 Claude 生态实现，不应被误读为“所有 Agent 都有同等能力”。

## 适合谁用

适合这几类任务：

1. 把零散经验沉淀成可复用 skill
2. 收缩已经写得过长、过硬编码、过拟合的 skill
3. 给 skill 建立更可复核的评测与人工 review 流程
4. 统一一个项目里多个 skill 的命名、结构和链接规则

## 版本

当前版本说明见 [VERSION.md](/Users/jixiaokang/.agents/skills/skills-master/VERSION.md)。
