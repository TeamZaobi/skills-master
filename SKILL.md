---
name: skills-master
description: Use for skill or agent lifecycle work, especially when the user wants to upgrade or update an existing skill, sync with upstream, merge local customizations, verify which copy/path is live, or then refactor, evaluate, package, or redistribute it. Trigger on requests like "upgrade skill", "update skill", "sync upstream", "which copy is live", "升级 skill", "更新 skill", and "同步上游".
---

# Skills Master

Use this skill to move a skill or companion agent project forward end to end. Do not treat it as a prompt-writing exercise only. Inspect the current repository, identify the user's stage, and choose the lightest workflow that will produce a defensible result.

## Trigger Coverage

Use this skill not only for authoring or rewriting, but also when the user wants to:

- upgrade an existing skill or agent from GitHub or another source
- compare an installed copy against upstream or against another local copy
- find which path, copy, symlink, or projected bundle is actually live in a tool
- relink, copy, package, or redistribute a skill or agent across tool directories
- audit whether a previous upgrade or install was done correctly

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

## Decide The Job

Classify the request into one primary mode before editing:

1. **Create**: there is no usable skill or agent yet.
2. **Upgrade or sync**: the asset exists and the user wants it refreshed from upstream, aligned across installs, or checked for version drift.
3. **Refactor**: the asset exists but the structure, guidance, or scope is weak.
4. **Document cleanup**: the repository drifted and the docs no longer match the real workflow.
5. **Evaluate**: the user wants test prompts, benchmarks, or side-by-side comparison.
6. **Optimize triggering**: the user wants better frontmatter descriptions and measurable trigger behavior for a skill.
7. **Install, link, package, or distribute**: the asset is done and needs linking, projection, packaging, or copy-based rollout.

If several modes apply, handle them in this order:

1. Identify the live asset and the editable source of truth
2. Fix repository truth or sync upstream
3. Fix skill or agent content
4. Add or repair evaluation
5. Optimize triggering when the asset is a skill
6. Verify installation mode, then package, copy, or link

## Audit Existing Claims First

When editing an existing skill, do not jump straight to wording tweaks.

First inspect the current text as a set of claims:

1. What does the skill say it does
2. What files, scripts, references, or workflows actually support those claims
3. Which claims are accurate
4. Which claims are stale, inflated, contradictory, or too broad
5. Which sections exist only because of previous patch-on-patch edits

Then act in this order:

1. Delete or rewrite unsupported claims
2. Rebuild the section around the true scope
3. Add constraints or trigger wording only if a local boundary still needs sharpening

Do not turn this audit into another generated preamble. It is a judgment step before editing, not an extra layer of prompt decoration.

## Capture Intent

When creating or reshaping a skill or agent, determine:

1. What job the asset should make easier
2. When it should trigger or be selected
3. What success looks like
4. What output format or artifacts matter
5. Whether the task benefits from formal evaluation or only qualitative review

Pull answers from the conversation and repository first. Ask follow-up questions only when the missing detail changes the implementation meaningfully.

## Upstream Preflight For Existing Assets

When the user wants to modify, optimize, or rewrite an existing skill or agent that may have come from GitHub, a marketplace, or another local clone, treat upstream checking as a default pre-edit step.

Do this before local optimization:

1. Decide whether the asset has a canonical upstream source.
   If the asset is purely local and intentionally private, you can skip this section.
2. Inventory meaningful local divergence first.
   Look for local trigger tuning, tool-specific adapters, personalized defaults, installation changes, or behavior changes the user relies on.
3. Check whether upstream changed recently enough to affect the local plan.
   Look for commits, tags, releases, layout changes, or installation guidance changes.
4. Fetch or download the latest upstream state into a comparison context.
   Prefer a separate branch, temporary clone, fetched ref, or unpacked snapshot over overwriting the local source in place.
5. Compare three things separately when they differ:
   the live asset, the editable source of truth, and the upstream source.
6. Decide the branch of work explicitly:
   merge upstream first, fork intentionally, or stay pinned to the current local version.
7. Only then start local refactor, optimization, or trigger rewriting.

Why this is a default strategy:

- You do not want to optimize a stale copy when upstream already solved the problem.
- You do not want to patch around a structure that changed upstream yesterday.
- You do not want to compare your rewrite against the wrong baseline.
- You do not want to erase local adaptations the user still depends on.

Do not turn this into cargo-cult checking:

- Skip it when the asset has no meaningful upstream.
- Skip it when the user explicitly wants a local-only fork and accepts the divergence.
- Keep the check lightweight when the user only needs a narrow local fix and upstream drift is unlikely to matter.

## Upgrade Or Sync Workflow

When the user asks to upgrade an existing skill or agent, do not treat it as a plain repository update.

The first simplification question is:

- Is there already a single editable source of truth that should be upgraded, while every other copy is just a live projection, symlink target, or packaged artifact?

If yes, prefer upgrading only that source and then verifying or refreshing the projections. Do not turn a one-source upgrade into a multi-copy editing task.

The second safety question is:

- Does that source contain local adaptations or personalized behavior that upstream does not know about?

If yes, do not overwrite it in place. Fetch the newest upstream copy separately, compare the deltas, and merge intentionally into the authoritative local source.

Work in this order:

1. Identify the live asset the tool is actually reading right now.
   Check whether the active path is a copy, symlink, generated projection, or workspace-local bundle.
2. Identify the editable source of truth that should be updated.
   Do not assume the live asset is the editable source.
3. Collapse avoidable complexity.
   If one source can remain authoritative, upgrade that source only.
   Treat other locations as projections to validate or regenerate, not as parallel places to hand-edit.
4. Protect local divergence.
   Inventory local adaptations before touching the source.
   Fetch or download upstream into a separate comparison context.
   Decide whether to merge, cherry-pick, port selected changes, or stay pinned.
5. Decide the upgrade mode.
   Development-maintenance mode can use symlinks or projections.
   Stable distribution mode should prefer copied bundles or explicit packaging over fragile path dependencies.
6. Update the single authoritative source using the chosen merge strategy.
7. Refresh the live install, link, or projection if the source layout changed.
8. Validate the result.
   Confirm the active path, version markers, and whether the tool needs a new session to rediscover the updated asset.

Two guardrails matter here:

- A repository being current does not mean the live skill or agent is current.
- If your upgrade plan requires hand-editing several copies, you probably modeled the source of truth incorrectly.
- If your upgrade plan would discard local adaptations before they are inventoried and merged, it is unsafe.
- Do not call the upgrade complete until the runtime consumer path has been checked.

## Authoring Rules

### Frontmatter

Every skill must have:

- `name`
- `description`

Every portable agent should have:

- `AGENT.md`
- `name`
- `description`

Optional fields such as `compatibility` are fine when they clarify real runtime requirements.

Write descriptions for triggering, not for marketing. The description should describe user intent, not only implementation details.

### Structure

Use the simplest structure that matches the task:

- **Workflow-based** for sequential jobs
- **Task-based** for collections of operations
- **Reference-based** for standards, policies, or long-lived guidance
- **Capability-based** for integrated systems with several related powers

Mix patterns only when it clearly improves usability.

### Progressive Disclosure

Use the source folder deliberately:

- `SKILL.md` for the main operating instructions
- `AGENT.md` for the main agent operating instructions
- `scripts/` for deterministic or repetitive execution
- `references/` for supporting material that should be loaded only when needed
- `assets/` for templates, boilerplates, and output-side files

If a reference file becomes large, add navigation hints or a small table of contents.

### Writing Guidance

- Explain why an instruction matters.
- Avoid brittle rule piles unless the task truly has hard constraints.
- Do not preserve inaccurate text by surrounding it with new caveats, exceptions, or negative trigger clauses.
- Prefer generalizable guidance over examples that only fit one test case.
- If the docs drifted because of multiple iterations, rewrite the affected section as a whole instead of appending more exceptions.
- If a section only survives because "all changes must be additive", question that premise and re-check the repository truth.

## Evaluation Workflow

Use the full loop only when it adds signal. For a small doc correction or a narrow rewrite, a lighter pass is usually better.

### When To Use Formal Evals

Formal evals are especially useful for:

- file transforms
- extraction workflows
- code generation with objective checks
- multi-step procedures with stable success criteria

Qualitative review is usually enough for:

- writing tone
- branding voice
- interface taste
- other subjective outputs

### Create The Eval Set

Store task prompts in `evals/evals.json`.

Use realistic prompts that a real user would actually send. Include relevant files when needed. Add assertions only when they are objectively checkable.

See `references/schemas.md` for the expected JSON structure.

### Run The Workspace Loop

Put results in a sibling workspace named `<skill-name>-workspace/`.

Organize by iteration:

```text
<skill-name>-workspace/
└── iteration-1/
    └── eval-0/
```

When the environment supports independent task execution, run the skill version and a baseline in the same iteration:

- New skill: compare `with_skill` against `without_skill`
- Existing skill rewrite: compare the new draft against a snapshot of the old skill

Create `eval_metadata.json` per eval directory. Capture timing data as soon as the environment exposes it.

### Grade And Aggregate

After runs finish:

1. Grade each run using `agents/grader.md` or an equivalent inline grading pass.
2. Aggregate the iteration with:

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

3. Read the benchmark for patterns, not just totals. Use `agents/analyzer.md` when you need a structured analyst pass.

### Human Review

Use the bundled viewer instead of inventing one-off review pages:

```bash
python eval-viewer/generate_review.py <workspace>/iteration-N --skill-name "my-skill"
```

If the environment is headless, use the static HTML mode supported by the viewer and collect `feedback.json` from the user afterward.

### Improve Without Overfitting

When revising after feedback:

- generalize from the complaint
- remove instructions that are not earning their keep
- look for repeated helper work that should become a bundled script
- avoid turning one stubborn edge case into a giant wall of rigid rules

Repeat the loop only while it produces meaningful improvement.

## Blind Comparison

When the user wants a more rigorous A/B comparison between two skill versions, use the comparison flow:

- `agents/comparator.md`
- `agents/analyzer.md`

This is optional. Do not force it into ordinary skill cleanup work.

## Trigger Description Optimization

This is a separate step. Only do it after the skill itself is already in reasonable shape.

### Important Boundary

The current trigger optimization scripts are **Anthropic / Claude specific**, not tool-agnostic. They rely on:

- `anthropic`
- `claude` CLI
- `.claude/commands`-based discovery behavior

If that stack is unavailable, skip this section rather than pretending it is portable.

### Prepare The Eval Queries

Create about 20 realistic queries:

- some should trigger
- some should not trigger
- the negative cases should be near misses, not obviously unrelated prompts

Use concrete, natural language that resembles real user requests.

### Review The Query Set

Use `assets/eval_review.html` when you want the user to edit or approve the trigger eval set before running the optimizer.

### Run The Loop

Prefer module execution for package-aware scripts:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-evals.json> \
  --skill-path <path-to-skill> \
  --model <active-model-id> \
  --max-iterations 5 \
  --verbose
```

This loop evaluates the current description, proposes revisions, and keeps history. It chooses the best result by held-out performance when a holdout split is enabled.

### Apply The Result

Take `best_description`, update the skill frontmatter, and show the before/after difference to the user with the measured scores.

## Linking And Packaging

Use one editable source of truth:

- user scope: `~/.agents/skills/<skill-name>`
- project scope: `<project-root>/.agents/skills/<skill-name>`
- user agent scope: `~/.agents/agents/<agent-name>`
- project agent scope: `<project-root>/.agents/agents/<agent-name>`

Link outward to tool-specific discovery folders instead of maintaining multiple editable copies.

### Initialize

```bash
python scripts/init_skill.py my-skill --path ~/.agents/skills
python scripts/init_agent.py review-agent --path ~/.agents/agents
```

### Link

```bash
python scripts/link_skill.py <skill-path>
python scripts/link_skill.py <skill-path> --status
python scripts/link_agent.py <agent-path>
python scripts/link_agent.py <agent-path> --status
```

### Validate

```bash
python -m scripts.quick_validate <skill-or-agent-path>
```

### Package

```bash
python -m scripts.package_skill <skill-path>
```

Package only after the skill content and metadata are stable enough to share. For agents, prefer rendering or linking to official tool directories instead of inventing a private package format.

### Official Tool Paths

When linking or projecting outward, prefer official default locations:

- Claude Code skills: `~/.claude/skills` and `.claude/skills`
- Claude Code agents: `~/.claude/agents` and `.claude/agents`
- OpenAI Codex skills: `~/.agents/skills` and `.agents/skills`
- OpenAI Codex agents: `~/.codex/agents` and `.codex/agents`
- Google Antigravity skills: `~/.gemini/antigravity/skills` and `<workspace-root>/.agents/skills`

If a tool is file-based rather than directory-based, render the smallest projection you can instead of hand-maintaining a second editable copy.

## Environment Adaptation

Do not assume every environment has the same features.

- If there are no subagents or parallel workers, run evals serially and lean more on human review.
- If there is no browser, export static HTML or present results inline.
- If there is no Anthropic stack, skip trigger optimization.
- If a tool cannot consume the canonical asset shape directly, generate a thin adapter rather than forking the source text.
- If the user only asked for documentation cleanup, do not drag them through benchmarking machinery they did not ask for.

## Reference Files

Read these only when they are relevant to the current task:

- `agents/grader.md`
- `agents/comparator.md`
- `agents/analyzer.md`
- `references/schemas.md`
- `references/workflows.md`
- `references/output-patterns.md`

## Final Check

Before you finish, confirm that:

1. The repository's main docs agree with the real workflow.
2. Platform-specific instructions are clearly labeled.
3. The guidance did not become longer just to preserve outdated history.
4. The user can tell what is stable, what is optional, and what is environment-bound.
5. For upgrade or install work, the live consumer path, install mode, and refresh requirements are explicit.
