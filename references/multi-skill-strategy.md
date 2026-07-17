# Multi-Skill Strategy

This document defines how to model, split, merge, and validate skills when more
than one skill could plausibly activate on the same request.

## Core Principle

Treat multi-skill collaboration as a routing problem with explicit ownership.

- One skill should own the primary user story.
- Secondary skills are optional collaborators, not hidden dependencies.
- Shared substeps belong in `scripts/`, `references/`, or other shared assets,
  not in sibling skills that must call each other.

## Skill Types

### Domain Skill

Owns a coherent task family with a stable user-facing trigger surface.

Use a domain skill when:

- the user can naturally ask for it directly
- the skill can deliver the main result by itself
- the skill has a clear source of truth and operating workflow

### Orchestration Skill

Coordinates or routes work across tools, workers, or adjacent skills.

Use an orchestration skill only when:

- coordination is itself the main job
- the orchestration rules are stable and reusable
- source-of-truth ownership is explicit
- `WHEN NOT TO USE`, handoff boundaries, and exit criteria are documented

### Shared Asset

Reusable logic that should not be a separate skill.

Prefer `scripts/`, `references/`, templates, or shared docs when several skills
need the same Step B.

Examples:

- a validator script
- a schema or policy reference
- a comparison rubric
- a projection helper

## Split Or Merge Checklist

Split into separate skills only when the candidate skill has:

- an independent user-facing trigger surface
- a workflow that remains useful without the sibling skill
- a meaningful reason to keep instructions, tooling, or authority separate

Merge overlapping skills when they:

- share the same source of truth
- repeatedly activate on the same queries
- differ mostly by internal step ordering rather than by user intent
- require the same reusable helper logic

## Coordination Shapes

### Primary Only

One skill owns the task. No secondary skill is required.

### Primary Plus Optional Secondary

One skill owns the task, while another skill may contribute a narrower capability.

Examples:

- research first, then rewrite the skill
- persistent planning alongside a long-running skill refactor
- GitHub metadata lookup while the primary task remains skill lifecycle work

Use the final deliverable to choose the primary owner:

- research report or evidence synthesis: the research skill is primary
- durable execution plan or status log: the planning skill is primary
- pull request, issue, CI, or review operation: the GitHub skill is primary
- product code, visual design, or user-facing behavior: the implementation
  skill is primary
- skill source, trigger, packaging, projection, or discovery change:
  `skills-master` is primary

When an adjacent skill contributes only evidence, planning, or transport, keep
it secondary and leave final-deliverable ownership with the primary skill.

### Orchestration

Use only when the coordination logic is the actual product.

Requirements:

- explicit source-of-truth ownership
- explicit handoff points
- explicit exit criteria
- explicit cases where orchestration should not be used

## Anti-Patterns

Avoid these:

- splitting every internal step into its own skill
- relying on implicit skill-to-skill calls
- making the primary skill unusable when a sibling skill is absent
- loading several overlapping skills just to share one reusable helper step
- orchestration without a `WHEN NOT TO USE` section
- parallel review courts on the same artifact without independent work boundaries

## Optional Metadata Convention

When multi-skill boundaries matter, a skill may include a simple `metadata`
frontmatter block for static tooling.

Example:

```yaml
metadata: |
  family: skill-lifecycle
  role: orchestrator
  coordination: primary-plus-optional-secondary
  adjacent_skills: deep-research, planning-with-files, github:github
```

Suggested keys:

- `family`: broad domain family such as `skill-lifecycle`, `research`, `planning`
- `role`: `domain` or `orchestrator`
- `coordination`: preferred coordination shape
- `adjacent_skills`: nearby skills worth checking in boundary evals

These keys are for linting and documentation. Do not make runtime behavior rely
on them being present.

## Validation Ladder

Use the cheapest validation that answers the question:

1. `quick_validate` for basic frontmatter and structure checks
2. `check_multi_skill_boundaries` for static overlap and orchestration checks
3. `trigger-evals.json` for single-skill trigger behavior
4. `boundary-evals.json` for adjacent-skill ownership and handoff cases
5. Dynamic client-side multi-skill tests only when static checks are no longer enough
