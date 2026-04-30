---
name: skills-master
description: Use for skill or agent lifecycle work, especially when the user wants to create, expand, update, compare, or test an existing skill or agent, sync with upstream, merge local customizations, verify which copy/path is live, measure with-skill versus without-skill quality, or package and redistribute it. Trigger on requests like "upgrade skill", "update skill", "add capability", "which copy is live", "E2E 测试", "增加能力", "更新 skill", "同步上游", "多工具支持", "检查路径", "sidecar adapter", "workflow adapter", and "multi-tool support".
---

# Skills Master

Use this skill to move a skill or companion agent project forward end to end. Do not treat it as a prompt-writing exercise only. Inspect the current repository, identify the user's stage, and choose the lightest workflow that will produce a defensible result.

## Trigger Coverage

Use this skill not only for authoring or rewriting, but also when the user wants to:

- upgrade an existing skill or agent from GitHub or another source
- add a new capability, mode, or workflow without letting the asset sprawl
- compare an installed copy against upstream or against another local copy
- measure whether a prompt, skill, or rewrite actually improves quality against a baseline
- find which path, copy, symlink, or projected bundle is actually live in a tool
- check **multi-tool support** (多工具支持) by verifying symlinks, projections, adapters, or upstream-installed bundles across `claude`, `codex`, `antigravity`, and sidecar workflow surfaces
- relink, copy, package, or redistribute a skill or agent across tool directories
- audit whether a previous upgrade or install was done correctly

When not to use: do not use this skill for ordinary product requirements, project source-of-truth governance, code implementation, data-plane runtime behavior, or visual generation unless the problem is specifically about the live skill or agent asset.

Multi-skill coordination: before absorbing adjacent skills, route narrow and handoff to the owner that already has the product, governance, runtime, visual, or domain mandate.

## Working Style

- Start from the actual repository state, not from inherited wording or remembered conventions.
- Prefer one editable source of truth. If the runtime can consume that source directly or through a thin projection, do not maintain extra editable copies.
- Treat local adaptations as real product decisions, not as disposable noise to be overwritten by upstream.
- When modifying an existing third-party or previously installed asset, check whether upstream changed before you optimize the local copy.
- Treat the current skill text as material to audit, not as a baseline that must be preserved.
- Use accessible language unless the user clearly wants technical shorthand.
- Prefer rewriting an outdated section cleanly over stacking more caveats onto it.
- Do not mistake respect for additive-only editing. If a claim is wrong, stale, or overbroad, delete or rewrite it.
- Separate portable guidance from platform-specific mechanics.
- When the user only wants a focused cleanup, do that directly instead of forcing the full evaluation loop.
- For meaningful modifications, upgrades, capability additions, or trigger rewrites, prefer controlled A/B E2E comparison over one anecdotal spot check.
- Prefer bounded empirical tightening over purely speculative rewriting when live behavior is cheap to probe.

## Low-Entropy Skill Governance

When `MyWay` or `files-driven` hands over a method-layer change, do not turn it into broad skill sprawl.
`skills-master` owns only the skill lifecycle part: live source, upstream/local divergence, projections, distribution, trigger behavior, and evaluation.

Use this causal chain before editing:

`user friction or capability gap -> live asset -> editable source of truth -> minimal behavior change -> verification / projection`

Rules:

1. If the current skill already behaves correctly when invoked, do not edit it just to record the conversation.
2. If the idea belongs to `MyWay`, `ProEng / product-engineer`, a project skill, a validator, or a runtime contract, route it there instead of duplicating it here.
3. Prefer updating one editable live source first; refresh public surfaces, packaged copies, or multi-host projections only when the user asks for rollout or the change affects discovery.
4. Add modes, workflows, test harnesses, or registry entries only when they reduce trigger drift, source-of-truth drift, verification cost, or future recovery risk.
5. If a skill governance pass only adds prose without changing live behavior, evaluation, projection correctness, or install/discovery safety, treat it as incomplete or unnecessary.

## Job Routing

Pick one primary mode before editing:

1. `create`
2. `upgrade_or_sync`
3. `expand_capability`
4. `refactor`
5. `document_cleanup`
6. `evaluate`
7. `optimize_triggering`
8. `install_link_package_or_distribute`

If several apply, handle them in this order:

`live asset / editable source -> repo truth or upstream sync -> skill content -> evaluation -> trigger optimization -> install / projection / package`

## Pre-Edit Gate

Before modifying an existing asset, inspect the current text as claims:

1. What does it say it does?
2. What files, scripts, references, or workflows support those claims?
3. Which claims are accurate, stale, inflated, contradictory, or patch-on-patch?
4. Which behavior must remain stable?
5. Is this narrow enough for a direct patch, or high-risk enough to require upstream / convergence work?

High-risk changes include core job, trigger boundary, adjacent-skill ownership, source-of-truth model, new modes, evaluation promises, or broad lifecycle changes.

If upstream may matter, inventory local divergence first, fetch or inspect upstream separately, then decide: merge, cherry-pick, stay pinned, or fork intentionally. Do not overwrite local adaptations in place.

## Core Workflows

### Upgrade Or Sync

1. Identify the live consumer path.
2. Identify the editable source of truth; do not assume it is the live path.
3. Treat copies, symlinks, public surfaces, generated bundles, and host projections as projections unless proven otherwise.
4. Protect local adaptations before importing upstream changes.
5. Update one authoritative source first.
6. Refresh links, packages, or projections only if layout or discovery changed.
7. Validate active path, version markers, and whether a new host session is needed.

Guardrail: a repository being current does not mean the live skill or agent is current.

### Expand Capability

1. State the smallest new job.
2. Check adjacent ownership before absorbing it.
3. Freeze non-goals.
4. Choose the lightest container: core `SKILL.md` only for core execution path; otherwise use `references/`, `scripts/`, `assets/`, or eval files.
5. Add at least one positive and one near-miss check before widening trigger behavior.
6. If behavior is stochastic, prompt-sensitive, or boundary-sensitive, use a controlled A/B E2E comparison.

### Refactor Or Cleanup

1. Delete or rewrite unsupported claims.
2. Rebuild the section around true scope.
3. Prefer one clean rewrite over stacking caveats.
4. Preserve live behavior unless the change explicitly intends to alter it.
5. Keep `SKILL.md` as live operating instructions; move background, variants, schemas, examples, and long rubrics to `references/`, `scripts/`, `assets/`, or `evals/`.

## Authoring Rules

- Frontmatter must include `name` and trigger-oriented `description`.
- Use `SKILL.md` / `AGENT.md` for core behavior, `scripts/` for deterministic work, `references/` for detail, `assets/` for reusable output material, and `evals/` for benchmark inputs.
- Prefer workflow-, task-, reference-, or capability-based structure; mix patterns only when it improves usability.
- Explain why constraints matter, but avoid brittle rule piles.
- Block tags are optional authoring hints, not a parser contract unless the repo ships a parser.

## Evaluation And Trigger Work

Use the cheapest reliable loop first:

`probe -> classify failure -> narrow edit -> re-test`

Use formal evals when they add signal: objective transforms, extraction, code generation, multi-step procedures, prompt-value comparisons, trigger boundary changes, or high-risk rewrites.

Controlled A/B rule:

- Freeze prompts and rubric before execution.
- Compare matched conditions such as `with_skill` vs `without_skill` or `old` vs `new`.
- Isolate contexts where possible; repeat stochastic runs.
- Score per prompt first, then aggregate.
- Treat one serious boundary regression as enough to reject a change.

Trigger optimization is separate from skill cleanup. Current trigger optimizer assumptions are Anthropic / Claude-specific; if that stack is unavailable, skip rather than pretending it is portable. Details live in `evals/`, `scripts/run_loop.py`, and `references/schemas.md`.

## Linking, Packaging, And Multi-Tool Adaptation

Do not guess multi-tool support by string-replacing paths inside `SKILL.md`.

Use one editable source of truth:

- user skill: `~/.agents/skills/<skill-name>`
- project skill: `<project-root>/.agents/skills/<skill-name>`
- user agent: `~/.agents/agents/<agent-name>`
- project agent: `<project-root>/.agents/agents/<agent-name>`

Asset shapes:

- native skill directory: link with `scripts/link_skill.py`
- native agent directory: link with `scripts/link_agent.py`
- multi-skill / plugin bundle: use upstream installer or host plugin mechanism first, then verify generated live paths
- command / workflow pack: install where the host expects it; create a thin adapter only when a host needs a trigger surface
- runtime / workflow engine: install as runtime; do not convert the whole engine into an always-on skill

Useful commands:

```bash
python3 scripts/link_skill.py <skill-path> --status
python3 scripts/link_agent.py <agent-path> --status
python3 -m scripts.quick_validate <skill-or-agent-path>
python3 -m scripts.package_skill <skill-path>
```

Prefer official host locations when projecting outward:

- Claude Code skills / agents: `~/.claude/skills`, `.claude/skills`, `~/.claude/agents`, `.claude/agents`
- Codex skills / agents: `~/.agents/skills`, `.agents/skills`, `~/.codex/agents`, `.codex/agents`
- Antigravity skills: `~/.gemini/antigravity/skills`, `<workspace-root>/.agents/skills`

Detailed multi-tool adaptation guidance lives in `references/multi-tool-adaptation.md`.

## Environment Adaptation

- No subagents or parallel workers: run evals serially and lean on human review.
- No browser: export static HTML or present results inline.
- No Anthropic stack: skip trigger optimization.
- Host cannot consume canonical asset directly: generate a thin adapter rather than forking the source text.
- External tool has its own installer, command registry, workflow directory, or runtime daemon: adapt to that surface instead of rewriting it into a local skill.
- User asked for focused cleanup: do not drag them through benchmarking machinery they did not request.

## Reference Files

Read only when relevant:

- `references/multi-tool-adaptation.md`
- `references/schemas.md`
- `references/workflows.md`
- `references/output-patterns.md`
- `references/adjacent-skills.md`
- `references/multi-skill-strategy.md`
- `evals/boundary-evals.json`
- `evals/trigger-evals.json`

## Final Check

Before finishing, confirm:

1. Main docs agree with the real workflow.
2. Platform-specific instructions are labeled.
3. The guidance did not grow just to preserve outdated history.
4. Stable, optional, and environment-bound parts are clear.
5. Upgrade / install work names the live consumer path, install mode, and refresh requirements.
