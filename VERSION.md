# Version

## Current

- Name: `skills-master`
- Version: `0.6.0`
- Status: lifecycle governance rebaselined on `writing-for-agents`
- Date: `2026-08-08`

## This Version Includes

- Narrow ownership: lifecycle delivery here; agent-facing writing and invocation design in `writing-for-agents`
- Minimal initializer with explicit `model` or `user` invocation mode
- Minimal companion-agent initializer with explicit projection only
- Host-specific invocation rendering for Claude-compatible frontmatter and Codex `agents/openai.yaml`
- Dated, source-linked discovery paths instead of durable host assumptions
- Fail-closed Kimi duplicate handling where public precedence is unspecified
- Explicit per-step completion-criterion audit and external rubric selection
- Deployment-local fleet policy with a tracked generic example
- Removal of the unverified `.claude/commands` description optimizer and its
  hard-coded writing rubric; behavior evaluation now remains with the
  agent-writing owner and target host

## Compatibility

- `init_skill.py --path` and project-native defaults remain supported.
- `skills/src/<name>` remains valid only for a declared generated product.
- `~/.codex/skills` is available only as the explicit `codex-compat` link target.
- Historical evaluation receipt schemas remain readable, but this lifecycle
  Skill no longer ships a host-specific description optimizer.
