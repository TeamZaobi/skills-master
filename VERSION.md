# Version

## Current

- Name: `skills-master`
- Version: `0.3.0`
- Status: skill / agent lifecycle maintenance with upstream-preflight and merge-first upgrade strategy
- Date: `2026-03-20`

## This Version Includes

1. 将项目主定位进一步扩展为“skill / agent 生命周期管理”，不再只强调创建与重写
2. 把“升级已有 skill / agent”补成一等触发场景，并前置到 `description`
3. 新增 upstream preflight 约束，要求优化已有外部资产前先检查上游变化
4. 明确单一真实源优先，反对把升级做成多副本并行编辑
5. 明确升级时应先获取最新 upstream 副本，再融合本地适应性和个性化修改
6. 将 live asset、source of truth、projection / copy / symlink 的区别写成显式工作流
7. 统一 README、`SKILL.md` 与版本说明对升级、融合、触发边界的描述

## Compatibility Notes

- skill / agent 设计、重写、校验、聚合、链接管理属于通用能力
- agent 投影与最小适配层管理已纳入当前版本主叙述
- upstream preflight、merge-first upgrade、single-source-of-truth 属于当前版本默认策略
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

这次需要升到 `0.3.0`，因为它不只是补几条说明，而是改了 `skills-master` 对“已有外部 skill / agent 如何升级与优化”的默认方法：

1. 触发描述从“创建 / 重写 skill”扩展到“升级 / 同步 / 判断哪份在生效”
2. 默认前置策略新增 upstream preflight，而不是直接在本地旧副本上开改
3. 升级动作从“直接同步”升级为“先取最新副本，再融合本地适应性修改”
4. 单一真实源、live asset、projection 的关系被提升为默认建模原则

因此用 `0.3.0` 标记一次生命周期与升级策略层面的升级更合适。

## Next Expected Version

建议下一次升版时机：

1. 增加明确的 trigger eval 集，覆盖 upgrade / sync / merge / live-copy 判断等场景
2. 为 skill 与 agent 的目录模板、投影策略提供更清晰的安装说明
3. 如果后续补齐非 Claude 的 trigger-eval 实现，再考虑进一步升小版本
