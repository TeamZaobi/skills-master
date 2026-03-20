# Version

## Current

- Name: `skills-master`
- Version: `0.2.0`
- Status: skill / agent baseline with claim-audit-first maintenance
- Date: `2026-03-20`

## This Version Includes

1. 将项目主定位扩展为“skills 与 companion agents 的工程与维护工具包”
2. 补充 agent 初始化、链接、投影相关能力的版本说明边界
3. 主文档明确采用 claim audit first 的维护顺序，而不是 additive-only 修补
4. 将“审计不是生成提示，而是编辑前判断动作”写成显式方法约束
5. 统一 README、`SKILL.md` 与版本说明对主路径的描述
6. 保留通用能力与 Anthropic / Claude 专用链路的边界说明

## Compatibility Notes

- skill / agent 设计、重写、校验、聚合、链接管理属于通用能力
- agent 投影与最小适配层管理已纳入当前版本主叙述
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

这次需要升到 `0.2.0`，因为它不只是文案修补，而是同时改了资产模型和默认维护方法：

1. 项目不再只覆盖 skill，也明确覆盖 companion agent
2. 默认维护顺序改为先审计 claim，再删改重写，再做局部边界优化
3. additive-only editing 被明确降格为需要避免的反模式

因此用 `0.2.0` 标记一次方法与范围的同步升级。

## Next Expected Version

建议下一次升版时机：

1. 增加明确的依赖清单或打包配置
2. 为 skill 与 agent 的目录模板、投影策略提供更清晰的安装说明
3. 如果后续补齐非 Claude 的 trigger-eval 实现，再考虑进一步升小版本
