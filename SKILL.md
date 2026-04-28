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

## Decide The Job

Classify the request into one primary mode before editing:

1. **Create**: there is no usable skill or agent yet.
2. **Upgrade or sync**: the asset exists and the user wants it refreshed from upstream, aligned across installs, or checked for version drift.
3. **Expand capability**: the asset exists and the user wants to add a new mode, workflow, or boundary-aware ability without turning it into a kitchen sink.
4. **Refactor**: the asset exists but the structure, guidance, or scope is weak.
5. **Document cleanup**: the repository drifted and the docs no longer match the real workflow.
6. **Evaluate**: the user wants test prompts, benchmarks, or side-by-side comparison.
7. **Optimize triggering**: the user wants better frontmatter descriptions and measurable trigger behavior for a skill.
8. **Install, link, package, or distribute**: the asset is done and needs linking, projection, packaging, or copy-based rollout.

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
5. What existing behavior must remain stable if you are adding or widening a capability
6. Whether the task benefits from formal evaluation or only qualitative review

Also decide whether the planned edit is narrow or high-risk enough to justify the stronger pre-edit preflight below.

Pull answers from the conversation and repository first. Ask follow-up questions only when the missing detail changes the implementation meaningfully.

## Pre-edit Preflight For Existing Assets

When the user wants to modify, expand, optimize, or rewrite an existing skill or agent, treat pre-edit preflight as the default decision gate before local optimization.

Run only the branches that add signal:

1. Decide whether the planned change is narrow or high-risk.
   Narrow wording fixes, obvious local bug fixes, and other low-risk cleanup usually do not need the stronger convergence branch.
2. Decide whether the asset has a canonical upstream source.
   If the asset is purely local and intentionally private, you can skip the upstream branch.
3. Run the relevant branch or branches below.
4. Only then start local refactor, optimization, or trigger rewriting.

### Upstream Branch

If the asset may have come from GitHub, a marketplace, or another local clone, do this before local optimization:

1. Inventory meaningful local divergence first.
   Look for local trigger tuning, tool-specific adapters, personalized defaults, installation changes, or behavior changes the user relies on.
2. Check whether upstream changed recently enough to affect the local plan.
   Look for commits, tags, releases, layout changes, or installation guidance changes.
3. Fetch or download the latest upstream state into a comparison context.
   Prefer a separate branch, temporary clone, fetched ref, or unpacked snapshot over overwriting the local source in place.
4. Compare three things separately when they differ:
   the live asset, the editable source of truth, and the upstream source.
5. Decide the branch of work explicitly:
   merge upstream first, fork intentionally, or stay pinned to the current local version.

### High-Risk Modification Convergence Branch

Use this stronger path when the change is likely to reshape the asset rather than just clean it up.

Typical triggers:

- the change affects the core job, trigger boundary, adjacent-skill ownership, or source-of-truth model
- the change adds a new capability, mode, or evaluation promise that could widen the surface area
- the request combines competing goals such as broader triggering and tighter boundaries
- the asset has meaningful local divergence and the edit direction is not obvious
- the work looks like a refactor or scope rewrite rather than a narrow fix

Run one short pass:

1. Freeze the user's original intent.
   Capture the job to preserve, the non-goals, and what must not break.
2. Audit claims and preflight context together.
   Reuse the earlier claim audit and any upstream or source-of-truth findings instead of restating them as a new preamble.
3. Run one round of adversarial questioning.
   Challenge whether the current plan fixes the real problem or only adds more rules, exceptions, or ritual around symptoms.
4. Write a convergence summary before editing.
   State what to keep, delete, rewrite, or defer, and answer explicitly: has this plan drifted away from the user's original intent?

Why this is a default strategy:

- You do not want to optimize a stale copy when upstream already solved the problem.
- You do not want to patch around a structure that changed upstream yesterday.
- You do not want to compare your rewrite against the wrong baseline.
- You do not want to erase local adaptations the user still depends on.
- You do not want a high-risk rewrite to drift away from the user's actual problem while looking more sophisticated on paper.

Do not turn this into cargo-cult process:

- Skip the upstream branch when the asset has no meaningful upstream.
- Skip the upstream branch when the user explicitly wants a local-only fork and accepts the divergence.
- Skip the convergence branch for narrow local fixes, obvious doc corrections, and other low-risk cleanup.
- Keep the whole preflight lightweight when the likely answer is already clear.

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

## Capability Expansion Workflow

When the user wants to add a new ability to an existing skill or agent, do not treat that as "just another paragraph to append."

Work in this order:

1. State the smallest new job that needs to be absorbed.
   Write it as a concrete ability, not as a vague ambition to be more helpful.
2. Check adjacent ownership before you absorb it.
   Ask whether an existing neighboring skill, script, reference file, or runtime adapter should own the work instead.
3. Freeze the non-goals.
   Record what the asset must still refuse, defer, or keep out of scope after the expansion.
4. Choose the lightest container.
   Put the new ability in the main skill only if it belongs on the core execution path. Otherwise prefer `references/`, `scripts/`, or `assets/`.
5. Add evaluation before you widen triggering.
   Create at least one positive case and one near-miss case that prove the new ability helps without collapsing the boundary.
6. If the new ability is prompt-sensitive, stochastic, or easy to overfit, run a controlled A/B E2E comparison against a baseline before calling it done.

The most common failure mode in capability expansion is not "missing detail." It is absorbing a new job without re-checking ownership, non-goals, and evaluation cost.

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

## Test-While-Editing Loop

When a skill change depends on real host behavior, tool behavior, model drift, or
evaluation results, do not finish the work in one speculative pass.

Use a bounded `test -> classify -> narrow edit -> re-test` loop.

This is lighter than full formal evals and often should happen before them.

### When To Use It

Use this loop when:

- the skill's claimed workflow depends on live behavior you can cheaply probe
- you are changing routing, prompt assembly, evaluation logic, or trigger wording
- a failure report is real but the root cause is still unclear
- you need to turn one-off observations into a durable skill rule without guessing

### Loop Shape

1. Choose the smallest representative probe.
   Prefer one narrow run or a few targeted variants over a large batch.
2. Observe and classify failure modes.
   Do not stop at "bad result"; decide whether the issue is structure, route,
   tool limitation, wording, or missing constraints.
3. Edit the narrowest layer that can explain the failure.
   This may be frontmatter, core workflow text, a reference file, a script, or a
   routing rule.
4. Re-run a targeted probe.
   Change one primary variable when possible so the result teaches you
   something.
5. Decide whether to continue, rewrite more deeply, or reroute.

### Guardrails

- Do not run a huge eval suite before the first cheap probe if a smaller test
  would expose the same problem faster.
- Do not keep appending caveats to a structurally wrong section; rewrite the
  section instead.
- Do not change several major variables at once and then claim a clean causal
  lesson.
- Keep one representative failure and one best-so-far result when they explain
  why the next edit happened.
- If repeated probes show a backend or tool limitation, document the boundary
  and change route instead of overfitting the skill text.
- If the same failure repeats twice in the same direction, strongly consider a
  route or structure change rather than more local patching.

### Structured Authoring: Combine Containers And Block Tags

Treat skill structure as a two-level system:

1. **Containers** separate large content roles and loading boundaries.
2. **Block tags** clarify the purpose of a section inside the chosen container.

Use containers first:

| Container | Put here | Why |
|-----|---------|-------------|
| `frontmatter` | Triggering metadata such as `name` and `description` | Loaded early for discovery and activation |
| `SKILL.md` body | The main workflow, decision rules, and critical operating guidance | Core execution path for the skill |
| `references/` | Detailed explanations, schemas, variants, and background material | Keeps the main skill lean |
| `scripts/` | Deterministic or repetitive execution logic | Improves reliability and reduces prompt bloat |
| `assets/` | Templates, boilerplates, and output-side resources | Keeps reusable artifacts out of instruction prose |
| `evals/` or structured JSON files | Test prompts, assertions, and benchmark inputs | Makes evaluation explicit instead of implied |

Then use block tags only when a container still needs finer semantic separation.

Suggested block tag fields:

| Field | Purpose |
|-----|---------|
| `kind` | What this block is doing: `workflow`, `decision`, `constraint`, `example`, `anti-pattern`, `rationale` |
| `stage` | Where it applies: `trigger`, `preflight`, `execution`, `validation`, `handoff` |
| `strictness` | How binding it is: `required`, `preferred`, `optional` |
| `audience` | Who the block is for: `agent`, `author`, `reviewer` |
| `load-when` | Optional hint for when to read the block or companion file |

Example:

~~~markdown
## Upstream Check

```skill-block
kind: decision
stage: preflight
strictness: required
audience: agent
```

If the asset has a meaningful upstream, check drift before local optimization.
~~~

Design rules:

- Prefer container boundaries over sentence-level tagging.
- Tag blocks sparingly; do not turn the whole skill into pseudo-XML or pseudo-JSON.
- Do not assume a file-wide default such as "all untagged text is output-form." Most skill prose is execution guidance, not product copy.
- If a section is mostly background or edge-case detail, move it into `references/` instead of wrapping it in local tags.
- Treat block tags as an authoring convention unless the repository also ships a parser, linter, or projection step that enforces them.

## Evaluation Workflow

Use the full loop only when it adds signal. For a small doc correction or a narrow rewrite, a lighter pass is usually better. For higher-leverage changes such as modifying, upgrading, expanding capability, or rewriting boundaries, prefer controlled A/B E2E comparison over a single spot check.

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

### Controlled A/B E2E Comparison For Skill Changes

When the user asks whether a prompt or skill actually helps, or when you are modifying, upgrading, or expanding an existing asset, use a controlled A/B E2E comparison if the answer could change the design direction.

1. Freeze the prompt set and scoring rubric before execution.
   Do not rewrite the benchmark after seeing early failures unless you explicitly restart the run.
2. Run matched conditions on the same prompts.
   Typical pairs are `with_skill` versus `without_skill`, or `new_skill` versus `old_skill`.
3. Isolate context per run.
   If subagents or fresh sessions are available, use a new isolated worker for every run so one condition cannot leak into another.
4. Repeat each prompt at least 3 times when the behavior is stochastic, wording-sensitive, or boundary-sensitive.
5. Keep the execution contract constant.
   Use the same model, same files, same artifact target, same response cap, and the same ban on meta commentary when that would contaminate scoring.
6. Treat uncontrolled pilots as pilots.
   If an early batch drifted in length, format, or leakage constraints, discard it instead of mixing it into the final benchmark.
7. Score per prompt first, then read the aggregate.
   Mean deltas matter, but a single boundary regression on one representative prompt can still invalidate the change.

Use this method for prompt-value questions because it is much harder to fool than a one-off "feels better" answer.

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

Use separate condition directories and repeated runs when you want statistical signal:

```text
<skill-name>-workspace/
└── iteration-1/
    └── eval-0/
        ├── with_skill/
        │   ├── run-1/
        │   ├── run-2/
        │   └── run-3/
        └── without_skill/
            ├── run-1/
            ├── run-2/
            └── run-3/
```

Create `eval_metadata.json` per eval directory or run directory. Capture timing data as soon as the environment exposes it. See `references/schemas.md` for recommended metadata fields.

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
- if the same failure pattern survives two local edits, reconsider the route,
  structure, or true scope instead of stacking more clauses

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

**Anti-pattern Warning:** When asked to check "multi-tool support paths" (多工具支持的路径), **DO NOT** attempt to guess and string-replace script paths inside `SKILL.md` (e.g. injecting `<SKILL_PATH>`). For native skills and agents, multi-tool support is determined by whether the asset is correctly linked or projected into the target tool discovery directories using `link_skill.py` or `link_agent.py`. For sidecar plugins, slash-command packs, or workflow runtimes, first identify the upstream install surface and then add only a thin local adapter if the host cannot consume that surface directly. Always run the relevant `--status` or live discovery check first.

Use one editable source of truth:

- user scope: `~/.agents/skills/<skill-name>`
- project scope: `<project-root>/.agents/skills/<skill-name>`
- user agent scope: `~/.agents/agents/<agent-name>`
- project agent scope: `<project-root>/.agents/agents/<agent-name>`

Link outward to tool-specific discovery folders instead of maintaining multiple editable copies.

### Multi-Tool Adaptation

Before linking or packaging, classify the asset shape:

- **Native skill directory**: a directory with one `SKILL.md`; link it with `link_skill.py`.
- **Native companion agent**: a directory with one `AGENT.md`; project or link it with `link_agent.py`.
- **Multi-skill or plugin bundle**: a repository that contains several skills, commands, or host metadata; use the upstream installer or host plugin mechanism first, then verify the generated live paths.
- **Command or workflow pack**: a command set, planning state, or workflow directory; install those files where the target tool expects them, and create a small adapter skill only when a host needs a trigger surface.
- **Runtime or workflow engine**: a CLI, MCP server, web service, or DAG executor; install the runtime as a runtime, keep project workflow files in the project, and do not convert the whole engine into an always-on skill.

If the asset is not a native skill or native agent, do not symlink the repository root into every tool. Preserve upstream as the canonical source, document the local projection, and make the adapter name the invocation path, version or commit, refresh command, and verification smoke.

Use `references/multi-tool-adaptation.md` when the task involves Superpowers-style plugins, GSD-style command packs, gstack-style skill suites, Archon-style workflow runtimes, or any external tool that is not a single local `SKILL.md`.

### Initialize

```bash
python3 scripts/init_skill.py my-skill --path ~/.agents/skills
python3 scripts/init_agent.py review-agent --path ~/.agents/agents
```

### Link

```bash
python3 scripts/link_skill.py <skill-path>
python3 scripts/link_skill.py <skill-path> --status
python3 scripts/link_agent.py <agent-path>
python3 scripts/link_agent.py <agent-path> --status
```

### Validate

```bash
python3 -m scripts.quick_validate <skill-or-agent-path>
```

### Package

```bash
python3 -m scripts.package_skill <skill-path>
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
- If an external tool has its own installer, command registry, workflow directory, or runtime daemon, adapt to that surface instead of rewriting it into a local skill by default.
- If the user only asked for documentation cleanup, do not drag them through benchmarking machinery they did not ask for.

## Reference Files

Read these only when they are relevant to the current task:

- `agents/grader.md`
- `agents/comparator.md`
- `agents/analyzer.md`
- `references/schemas.md`
- `references/workflows.md`
- `references/output-patterns.md`
- `references/multi-tool-adaptation.md`

## Final Check

Before you finish, confirm that:

1. The repository's main docs agree with the real workflow.
2. Platform-specific instructions are clearly labeled.
3. The guidance did not become longer just to preserve outdated history.
4. The user can tell what is stable, what is optional, and what is environment-bound.
5. For upgrade or install work, the live consumer path, install mode, and refresh requirements are explicit.
