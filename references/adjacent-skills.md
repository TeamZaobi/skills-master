# Adjacent Skills And Handoffs

This document gives practical handoff boundaries for neighboring skill
families that commonly sit near skill or agent lifecycle work.

## Skill Lifecycle Governance

Primary family: `skills-master`

Use this family when the main job is:

- creating, upgrading, or refactoring a skill or companion agent
- cleaning up `SKILL.md`, `AGENT.md`, README, or install topology
- deciding source of truth, projections, packaging, or link strategy
- optimizing trigger boundaries or eval coverage for a skill

Do not make this family primary when the main job has moved elsewhere.

## Research Skills

Examples:

- `deep-research`
- `web-research`

Make research primary when the requested deliverable is a research report,
comparison, or evidence synthesis.

Make research secondary when:

- the main deliverable is still a skill or agent rewrite
- research is only needed to inform trigger wording, benchmarks, or workflow choices

## Planning Skills

Examples:

- `planning-with-files`
- `planning-with-files-zh`

Make planning primary when the requested deliverable is a durable plan, ongoing
status log, or file-based execution memory.

Make planning secondary when the primary job remains lifecycle work on a skill
or agent and the plan is just support infrastructure.

## GitHub Operational Skills

Examples:

- `github:github`
- `github:gh-address-comments`
- `github:gh-fix-ci`

Make GitHub operations primary when the main job is:

- triaging pull requests or issues
- fixing CI
- addressing review comments
- publishing branches or PRs

Keep lifecycle governance primary when GitHub is only the source of truth lookup
or transport layer for a skill upgrade or repo comparison.

## Frontend Or Product Implementation Skills

Examples:

- `frontend-design`
- `ui-ux-pro-max`

Make implementation skills primary when the main deliverable is product code,
visual design, or user-facing behavior.

Keep lifecycle governance primary only when the main job is reshaping the skill
or agent that supports those tasks.

## Handoff Rules

Use these default rules:

- If another skill owns the final deliverable, hand off rather than expanding this skill's scope.
- If the neighboring skill only contributes evidence, planning, or metadata, keep it secondary.
- If the same query routinely needs the same pair of skills, add a boundary eval case.
- If the same helper step keeps appearing in both skills, move it into a shared asset.
