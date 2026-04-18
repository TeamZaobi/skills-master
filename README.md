# Skills Master

`skills-master` 不是面向某个业务领域的 skill，也不是一个泛化的 agent 工具箱。

它的真正开发目的很简单：**把“开发 skill 与 companion agent 这件事”本身做成一个可复用的 skill**。也就是说，当 agent 需要创建、重写、收缩、评估或治理其他 skills，或者需要搭建、修造、投影其他 agents 时，这个 skill 提供方法、结构和配套资源。

## 这个仓库究竟是什么

这个仓库是 `skills-master` 这个 meta-skill 的源码与配套资源。

它服务的不是终端业务任务，而是下面这些“skill / agent 开发任务”：

1. 从零创建一个新 skill
2. 升级一个已安装的 skill 或 agent，并确认当前真正生效的是哪份资产
3. 给现有 skill 增加新能力，但不让边界和主职责失控
4. 重写已经过拟合、堆规则、越改越乱的 skill
5. 清理失真的说明文档，让 README、`SKILL.md`、脚本能力重新一致
6. 给 skill 建立评测、人工 review、对比基线和迭代闭环
7. 优化 skill 的触发描述与结构组织
8. 为 agents 建立单一真实源、跨工具投影与最小适配层
9. 统一多个工具环境下的真实源、链接与分发方式

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

1. 先识别当前任务属于创建、升级、重写、文档校正、评测、触发优化还是分发
2. 先确认 live asset 和 editable source of truth 不是同一件事
3. 对已有 skill / agent，先做一次 pre-edit preflight，再决定本地怎么改
4. 如果资产有 meaningful upstream，先检查 upstream 最近有没有变化
5. 如果这次修改是高风险重写，先冻结初心、审 claim、做一轮对抗质询，再落笔
6. 如果唯一真实源已经存在，优先只升级那一份，不要把升级做成多副本同步
7. 但升级这唯一真实源时，也要先拿到最新 upstream 副本做比较，再融合本地适应性和个性化修改
8. 先修正仓库真实情况，再修 skill 或 agent 内容，再补评测与分发
9. 先把现有文档当成待审 claim 集，而不是默认正确的底稿
10. 避免补丁式叠说明，尽量整段重写失真的 section
11. 不要把“尊重原文”误写成“所有修改都必须 additive”
12. 只在真的重复、脆弱、需要确定性时才把能力下沉到 `scripts/`
13. 把通用方法和平台专用机制分开写清楚
14. 对修改、升级、加能力和评测，优先用上下文隔离的 A/B E2E 对比，而不是靠一次主观试跑判断提示词值不值
15. 用尽可能少但足够的结构，让 skill 或 agent 可长期维护，而不是只对几个样例有效

## 一个需要避免的反模式

维护 skill 或 agent 文档时，最常见的错误不是“删得太多”，而是：

- 先假设现有表述基本正确
- 把所有失败都理解成边界不够精细
- 然后继续补限制词、否定句、例外项和 trigger 条件

这样会让文档越来越厚，但真实问题没有被解决，因为原来的 claim 可能已经失真、过宽或过时。

更可靠的顺序是：

1. 先列出现有文档到底声称了什么
2. 再检查这些声称是否被仓库里的脚本、文件、流程和真实用途支撑
3. 删除或重写不成立的 claim
4. 只有在真实边界已经稳定后，才做局部约束和触发优化

也就是说，**审计不是一段新的生成提示，而是编辑开始前的判断动作**。

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
- 做多-skill 边界的静态检查

### `references/`

提供可按需读取的技能设计参考，例如工作流模式、输出模式、JSON 结构约定，以及多-skill 的拆分与 handoff 策略。

### `agents/`

提供评分、对比、分析这类辅助角色说明，用于评测和迭代阶段。

### `eval-viewer/`

提供人工 review 界面生成能力，帮助人类快速查看不同迭代的输出与 benchmark。

## 这个 skill 的主路径

如果按真正用途来理解，本项目的默认使用路径应该是：

1. 识别一个已有或待创建的 skill 或 agent 是否需要被重做
2. 审计它当前文档中的 claim 哪些真实、哪些漂移、哪些过度表述
3. 阅读或改写它的 `SKILL.md` 或 `AGENT.md`
4. 决定哪些内容该留在主文档，哪些该下沉到 `scripts/`、`references/`、`assets/`
5. 如果这次修改会影响边界、能力面或提示词价值，先配一组隔离上下文的对比测试
6. 必要时补评测集和人工 review 流程
7. 在确认结构稳定后，再考虑触发优化、链接、投影和打包

也就是说，**先有 skill / agent 设计与治理，后有脚本与发布动作**。不要把顺序倒过来。

## 多-Skill 协同怎么处理

这里的默认策略不是“把每个子步骤都拆成 skill”，而是：

1. 先找出主用户故事，由一个 primary skill 对最终结果负责
2. 只有当另一个 skill 提供了独立能力，且 primary skill 不该吞掉它时，才让它作为 secondary skill 协同
3. 如果多个 skills 共享同一个可复用子步骤，就把它下沉到 `scripts/` 或 `references/`，不要做成隐式 skill 依赖
4. 如果几个 micro-skill 常在同类 query 上一起触发，还共享同一真实源，就应该合并成一个 domain skill，在内部 route
5. orchestration skill 必须显式写出 `WHEN NOT TO USE`、handoff 边界、exit criteria 和 source-of-truth 归属

仓库里的配套文件：

- `references/multi-skill-strategy.md`：多-skill 的拆分、合并和协同策略
- `references/adjacent-skills.md`：常见邻接 skill 家族的 handoff 边界
- `evals/boundary-evals.json`：多-skill 边界样例
- `scripts/check_multi_skill_boundaries.py`：静态边界检查器

## 一个经常被漏掉的触发场景

当用户说下面这些话时，`skills-master` 也应该触发，而不该被当成普通仓库维护：

- “先升级这个 skill”
- “看看 GitHub 有没有新版并同步到 Codex / Claude”
- “确认本机现在生效的是哪一份 skill”
- “把这个 skill 重新链接到另一个工具目录”

原因很简单：这类任务的关键不是 `git pull`，而是 skill / agent 生命周期管理。真正要先分清的是：

- 哪一份是当前工具正在读取的 live asset
- 哪一份是应该编辑的 source of truth
- 当前安装是 copy、symlink 还是 projection
- 升级后是否需要刷新入口、重建 bundle，或者开新会话让工具重新发现

如果这些问题没先澄清，“源码仓库升级了”并不等于“用户正在使用的 skill 已经升级”。

## 为什么改一个已有 skill 时要先做 pre-edit preflight

这一步不该只剩“先看 upstream”。很多时候，用户嘴上说的是“优化一下这个 skill”“帮我改触发条件”“重写成更适合 Codex 的版本”，真正容易出问题的并不只有版本漂移，还包括修改方向本身是否已经偏离了用户原始意图。

所以更稳的默认顺序不是“先改，再看要不要同步”，而是先做一次 `pre-edit preflight`。这个 preflight 有两个按需分支：

- `upstream branch`：当这个 skill 本来就有 canonical upstream 时，先确认最近的 upstream 变化会不会影响当前修改方向
- `high-risk convergence branch`：当这次修改会影响核心 job、trigger boundary、adjacent-skill ownership 或 source-of-truth 建模时，先做一次短收敛，再决定怎么改

### upstream branch

这一步不该只出现在“升级”任务里。只要这个 skill 有上游源，它就可能影响当前修改计划。

原因通常有几个：

- 上游可能已经修了你正准备本地修的问题
- 上游可能刚改了目录结构、安装方式或描述边界，你基于旧副本优化会偏掉
- 你想比较“本地要不要改”，前提是先知道自己在跟什么基线比较
- 源里可能已经有本地适应性和个性化修改，直接同步会把它们冲掉

更稳的顺序通常是：

1. 先确认这个 skill 有没有 canonical upstream
2. 如果有，先看最近的 upstream 变化会不会影响当前修改方向
3. 再决定是先同步、明确分叉，还是保持本地 pin 住不动
4. 之后才开始真正的重写、优化或触发调整

当然，这不是死规则：

- 纯本地私有 skill 可以跳过
- 用户明确要做本地 fork，也可以跳过
- 很小的局部修补，如果 upstream 漂移明显不相关，可以轻量检查后继续

### 高风险修改收敛 branch

如果这次修改不是小修小补，而是会改动 skill 的主职责、触发边界、邻接 skill 归属，或者真实源建模，那就不该一上来直接写。

更可靠的顺序是：

1. 先冻结用户原始意图，写清楚这次修改要保留什么、不能破坏什么
2. 把 claim 审计和 preflight 发现放到一起看，而不是拆成新的仪式性前言
3. 做一轮对抗质询，确认当前方案是在修真实问题，而不是继续补规则、补例外、补角色
4. 先写一份收敛摘要，再进入真正编辑

也就是说，默认心智应该是：**改已有 skill 之前，先做一次 pre-edit preflight；有 upstream 时走 upstream branch，高风险修改时再加收敛 branch。**

## 升级已有 skill / agent 时

对这类任务，推荐顺序应该是：

1. 先确认当前工具实际读取的是哪份安装资产
2. 再确认哪份目录才是可编辑的真实源
3. 如果唯一真实源已经存在，就只升级这一份
4. 先盘点这份真实源里有哪些本地适应性和个性化修改
5. 先把最新 upstream 副本取下来放到比较上下文里，不要直接覆盖本地真实源
6. 比较 upstream、新真实源、live asset 三者差异
7. 再决定是 merge、挑拣移植，还是继续 pin 住本地版本
8. 其他路径只当 link、copy 或 projection 来验证或刷新，不要并行手改
9. 判断这次是开发维护安装，还是稳定分发安装
10. 更新唯一真实源
11. 刷新 link、copy 或 projection
12. 验证 active path、版本标记，以及是否需要新会话

一个很实用的自检问题是：

- 如果当前升级方案要求你手工处理多份看起来内容相近的 skill 副本，那大概率是 source-of-truth 建模做错了。
- 如果当前升级方案会在盘点本地差异之前直接覆盖真实源，那大概率是 merge 策略做错了。

## 给人的入口

如果你是人类维护者，先看这几个文件：

1. [SKILL.md](SKILL.md)
2. [references/workflows.md](references/workflows.md)
3. [references/output-patterns.md](references/output-patterns.md)
4. [references/schemas.md](references/schemas.md)
5. [references/multi-skill-strategy.md](references/multi-skill-strategy.md)
6. [references/adjacent-skills.md](references/adjacent-skills.md)

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
python3 -m scripts.check_multi_skill_boundaries ~/.agents/skills --boundary-evals /path/to/skill/evals/boundary-evals.json
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
- 多-skill 边界检查目前先是静态 checker，动态同场实测仍需后补

这些都是配套层面的限制，不影响本项目作为“skill / agent 开发 skill”的主定位。

## 版本

当前版本说明见 [VERSION.md](VERSION.md)。
