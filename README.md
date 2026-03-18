# Skills Master

`skills-master` 不是面向某个业务领域的 skill，也不是一个泛化的 agent 工具箱。

它的真正开发目的很简单：**把“开发 skill 与 companion agent 这件事”本身做成一个可复用的 skill**。也就是说，当 agent 需要创建、重写、收缩、评估或治理其他 skills，或者需要搭建、修造、投影其他 agents 时，这个 skill 提供方法、结构和配套资源。

## 这个仓库究竟是什么

这个仓库是 `skills-master` 这个 meta-skill 的源码与配套资源。

它服务的不是终端业务任务，而是下面这些“skill / agent 开发任务”：

1. 从零创建一个新 skill
2. 重写已经过拟合、堆规则、越改越乱的 skill
3. 清理失真的说明文档，让 README、`SKILL.md`、脚本能力重新一致
4. 给 skill 建立评测、人工 review、对比基线和迭代闭环
5. 优化 skill 的触发描述与结构组织
6. 为 agents 建立单一真实源、跨工具投影与最小适配层
7. 统一多个工具环境下的真实源、链接与分发方式

如果一句话概括：**它是“用来开发和维护其他 skills 与 companion agents 的 skill”。**

## 它不是什么

为了避免继续写偏，这个仓库不应该被描述成：

- 一个通用的多 Agent 框架
- 一个以脚本集合为核心的 automation 仓库
- 一个主要目标是打包 `.skill` 文件的发布工具
- 一个围绕某个平台历史遗留语义展开的兼容层

脚本、viewer、reference 文档都只是配套资源。主语始终应该是这个 skill 本身，以及它如何帮助 agent 更好地开发别的 skills 与 companion agents。

## 核心方法

`skills-master` 的核心方法不是“多写规则”，而是：

1. 先识别当前任务属于创建、重写、文档校正、评测、触发优化还是分发
2. 先修正仓库真实情况，再修 skill 或 agent 内容，再补评测与分发
3. 避免补丁式叠说明，尽量整段重写失真的 section
4. 只在真的重复、脆弱、需要确定性时才把能力下沉到 `scripts/`
5. 把通用方法和平台专用机制分开写清楚
6. 用尽可能少但足够的结构，让 skill 或 agent 可长期维护，而不是只对几个样例有效

## 仓库里的东西各自负责什么

### `SKILL.md`

这是核心。它定义了 agent 在处理“skill / agent 开发任务”时应该如何思考、分流、重写、评测和迭代。

### `scripts/`

这些脚本不是仓库的目的，而是为 meta-skill 提供支撑：

- 初始化 skill / agent
- 校验 skill / agent 结构
- 管理链接
- 打包 skill
- 渲染 Codex agent 投影
- 聚合 benchmark
- 在特定平台里做触发描述评测

### `references/`

提供可按需读取的技能设计参考，例如工作流模式、输出模式、JSON 结构约定。

### `agents/`

提供评分、对比、分析这类辅助角色说明，用于评测和迭代阶段。

### `eval-viewer/`

提供人工 review 界面生成能力，帮助人类快速查看不同迭代的输出与 benchmark。

## 这个 skill 的主路径

如果按真正用途来理解，本项目的默认使用路径应该是：

1. 识别一个已有或待创建的 skill 或 agent 是否需要被重做
2. 阅读或改写它的 `SKILL.md` 或 `AGENT.md`
3. 决定哪些内容该留在主文档，哪些该下沉到 `scripts/`、`references/`、`assets/`
4. 必要时补评测集和人工 review 流程
5. 在确认结构稳定后，再考虑触发优化、链接、投影和打包

也就是说，**先有 skill / agent 设计与治理，后有脚本与发布动作**。不要把顺序倒过来。

## 给人的入口

如果你是人类维护者，先看这几个文件：

1. [SKILL.md](SKILL.md)
2. [references/workflows.md](references/workflows.md)
3. [references/output-patterns.md](references/output-patterns.md)
4. [references/schemas.md](references/schemas.md)

其中：

- `README.md` 解释这个仓库为什么存在
- `SKILL.md` 才是 agent 真正执行时要遵循的说明

## 配套脚本

只有在需要时再使用这些脚本，不要把它们当成项目目的：

```bash
python3 scripts/init_skill.py my-skill --path ~/.agents/skills
python3 scripts/init_agent.py review-agent --path ~/.agents/agents
python3 -m scripts.quick_validate /path/to/my-skill
python3 scripts/link_skill.py /path/to/my-skill --status
python3 scripts/link_agent.py /path/to/review-agent --status
python3 -m scripts.package_skill /path/to/my-skill
python3 -m scripts.aggregate_benchmark /path/to/workspace/iteration-1 --skill-name my-skill
```

## 依赖边界

### 通用能力

下面这些能力是本仓库的常规部分：

- skill 结构设计
- agent 结构设计
- 文档重写
- 初始化、校验、链接、打包、benchmark 聚合

最小依赖：

- Python `3.9+`

### 平台专用增强能力

触发描述优化相关脚本目前仍然依赖 Anthropic / Claude 生态：

- `anthropic`
- `claude` CLI
- 对应认证环境

```bash
python3 -m pip install anthropic
python3 -m scripts.run_eval --help
python3 -m scripts.run_loop --help
```

如果这部分环境不存在，不影响本仓库作为 meta-skill 的主要用途。

## 当前状态

这个仓库现在已经完成一轮从“继承型文档”到“按真实目的重述”的整理，但仍有一些明确边界：

- 还没有统一的 `requirements.txt` 或 `pyproject.toml`
- 部分脚本更适合以 `python3 -m scripts.<name>` 方式运行
- 触发优化链路仍然不是跨平台实现

这些都是配套层面的限制，不影响本项目作为“skill / agent 开发 skill”的主定位。

## 版本

当前版本说明见 [VERSION.md](VERSION.md)。
