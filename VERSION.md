# Version

## Current

- Name: `skills-master`
- Version: `0.1.1`
- Status: documentation realignment baseline
- Date: `2026-03-16`

## This Version Includes

1. 将项目主定位重新收口为“skills 工程与维护工具包”
2. 主文档不再默认沿用继承自 Claude 的叙事方式
3. 把通用能力与 Anthropic / Claude 专用能力明确拆开
4. 统一主入口文档、skill 本体说明与版本说明的边界
5. 补充当前脚本调用方式与真实源/链接策略说明

## Compatibility Notes

- skill 设计、重写、校验、聚合、打包、链接管理属于通用能力
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

虽然这次不是功能大改，但它修正的是项目认知边界：

1. 什么是默认主路径
2. 什么只是平台专用增强能力
3. 什么属于历史遗留表达而不应继续扩散

因此用 `0.1.1` 标记一次文档与语义基线校正。

## Next Expected Version

建议下一次升版时机：

1. 增加明确的依赖清单或打包配置
2. 为通用能力与平台专用能力提供更清晰的安装说明
3. 如果后续补齐非 Claude 的 trigger-eval 实现，再考虑进一步升小版本
