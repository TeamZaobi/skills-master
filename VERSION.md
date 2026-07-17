# Version

## Current

- Name: `skills-master`
- Version: `0.5.0`
- Status: self-governed multi-host skill and companion-agent lifecycle
- Date: `2026-07-17`

## This Version Includes

- Four explicit asset shapes with deterministic canonical paths
- Repository-product layout at `skills/<name>`
- Registry v2 for canonical sources, projections, and external dependencies
- Direct one-hop host projection rules
- Shared `.agents/skills` plus opt-in Kimi Code projection and shadow checks
- Repository topology doctor and layout fixtures
- A compact four-step `SKILL.md` with conditional detail disclosed to references
- Explicit external method-skill and adjacent-skill ownership boundaries

## Compatibility

- Existing `init_skill.py --path` and project-native defaults remain supported.
- `skills/src/<name>` remains valid only for a declared generated product.
- `doctor.py` applies to registry-backed repositories; standalone assets use
  `quick_validate` and direct link status.
- Claude-specific trigger evaluation remains optional; core lifecycle tooling
  does not depend on it.
