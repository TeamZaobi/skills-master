# Version

## Current

- Name: `skills-master`
- Version: `0.3.1`
- Status: skill / agent lifecycle maintenance with structured authoring, upstream-preflight, and merge-first upgrade strategy
- Date: `2026-03-21`

## This Version Includes

1. 将项目主定位进一步扩展为“skill / agent 生命周期管理”，不再只强调创建与重写
2. 把“升级已有 skill / agent”补成一等触发场景，并前置到 `description`
3. 新增 upstream preflight 约束，要求优化已有外部资产前先检查上游变化
4. 明确单一真实源优先，反对把升级做成多副本并行编辑
5. 明确升级时应先获取最新 upstream 副本，再融合本地适应性和个性化修改
6. 将 live asset、source of truth、projection / copy / symlink 的区别写成显式工作流
7. 统一 README、`SKILL.md` 与版本说明对升级、融合、触发边界的描述
8. 将内联 `meta` 注释式设计改写为“容器优先 + 块级标签补充”的结构化写法
9. 明确 `frontmatter`、`SKILL.md`、`references/`、`scripts/`、`assets/`、`evals/` 的职责分工
10. 去掉“未标注文本默认 target-form”这类文件级默认语义，改为显式、局部、可收敛的块级标签约定

## Compatibility Notes

- skill / agent 设计、重写、校验、聚合、链接管理属于通用能力
- agent 投影与最小适配层管理已纳入当前版本主叙述
- upstream preflight、merge-first upgrade、single-source-of-truth 属于当前版本默认策略
- structured authoring 默认采用容器分流，块级标签只作为补充语义
- `run_eval.py`、`run_loop.py`、`improve_description.py` 仍属于 Anthropic / Claude 专用链路
- 工具侧链接目标仍然保留 `claude`、`codex`、`antigravity`
- 历史兼容信息保留，但不再作为默认工作流叙述

## Naming History

1. `skill-creator`
   早期名称，强调“创建单个 skill”
2. `skill-master`
   开始覆盖创建之外的治理动作
3. `skills-master`
   当前名称，强调面向整个 skills 体系

## Why This Bump

这次需要升到 `0.3.1`，因为它在 `0.3.0` 的生命周期与升级策略之上，又补了一次明确的结构设计修正：

1. 不再把 `meta` 设计成文件内的默认语义系统，而是回到社区更稳定的容器化组织
2. 在容器分流的基础上，允许用少量块级标签表达 `workflow`、`decision`、`constraint` 等局部语义
3. 明确这类标签首先是作者约定，不假定仓库已经有解析器、linter 或 projection 去强制执行
4. 让结构化设计更贴近 `skills-master` 当前仓库已经存在的 `references/`、`scripts/`、`assets/` 与 eval 工作流

因此更合适的标记是一次补丁升级到 `0.3.1`，而不是继续沿用 `0.3.0` 的版本描述。

## Next Expected Version

建议下一次升版时机：

1. 增加明确的 trigger eval 集，覆盖 upgrade / sync / merge / live-copy 判断等场景
2. 为 skill 与 agent 的目录模板、投影策略提供更清晰的安装说明
3. 如果后续补齐非 Claude 的 trigger-eval 实现，再考虑进一步升小版本
