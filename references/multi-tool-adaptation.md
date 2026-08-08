# Multi-Tool Adaptation

Use this reference when a skill or agent lifecycle task involves more than one host tool, or when an upstream project is not a single native `SKILL.md` directory.

## Goal

Keep one canonical owner for the external capability while making each host consume the smallest compatible surface.

Select the canonical location with
[`layout-contract.md`](layout-contract.md) before creating projections. A
repository-owned distributable skill uses `skills/<name>`; project host paths
remain direct read-only projections. Host paths and invocation controls drift;
use [`host-contracts.md`](host-contracts.md) as the dated, source-linked
snapshot and reverify it before changing a projection. When Kimi sees the same
name through `.agents/skills` and `.kimi-code/skills`, require both entries to
resolve to one canonical realpath because public precedence is unspecified.

The adaptation should answer:

- What job is the tool actually solving, and do official manuals, installed examples, or community practice already show the expected integration path?
- What is the upstream source of truth?
- What does each host actually discover or execute?
- Is the local asset a source, symlink, projection, thin adapter, generated bundle, or runtime install?
- How is it refreshed?
- How is live discovery verified after install?

Before adapting a tool, run a small intake pass instead of starting from installation:

1. Check the official manual, source, CLI help, configuration examples, and release notes.
2. Check the local installed instance or project-local workflow if one already exists.
3. Check mature community practice and known anti-patterns when the tool ecosystem is active.
4. Separate official mechanism, live instance, community experience, and current inference.

### Method Skills

Treat TDD, BDD, review, research, and other method skills as method
capabilities. They retain authority over their method; lifecycle work retains
authority over source and delivery. Project truth remains with the repository's
declared governance owner.

## Skill And Plugin Catalog

Any discovered or candidate skill, plugin, connector, app, MCP surface, CLI,
command pack, workflow runtime, or browser adapter can enter this intake path.

For an existing host-discovered skill:

- If the user's task simply matches the skill, use the skill normally.
- Route wording, completion criteria, and invocation design to
  `writing-for-agents`; route install location, upstream pin, generated
  projection, host discovery, and distribution here.
- If the skill's output becomes project truth, hand acceptance to the
  repository's declared governance owner.
- If the skill depends on an external ecosystem, check official manuals, installed examples, and mature community practice before writing a custom adapter.

## Asset Shapes

### Native Skill

Shape: one directory whose main contract is `SKILL.md`.

Default action: keep one editable source, then use `scripts/link_skill.py` for supported hosts.

Required check: run `link_skill.py <path> --status`, then open a fresh host session if the host caches discovery.

For a registry v2 repository, prefer:

```bash
python3 scripts/link_skill.py --registry skills/registry.toml --all
python3 scripts/doctor.py <project-root>
```

Repository-local Markdown links that leave a Skill package remain warnings by
default. When such a link is an intentional dependency on a project truth
source, declare its repository-relative path or glob under
`policy.project_local_markdown_allowlist` in registry v2. The allowlist does not
permit missing targets or paths outside the repository.

### Native Companion Agent

Shape: one directory whose main contract is `AGENT.md`.

Default action: keep one editable source, then use `scripts/link_agent.py` or the host's official agent projection.

Required check: run `link_agent.py <path> --status`, then verify that the target host can see the rendered agent.

### Multi-Skill Or Plugin Bundle

Shape: one upstream repository contains multiple skills, host plugin metadata, commands, hooks, or scripts.

Default action: use the upstream installer or host plugin mechanism. Do not symlink the repository root as if it were one skill.

Local adaptation: add a thin adapter only if the host needs one routing
surface. Its agent-facing text follows `writing-for-agents`; its lifecycle
metadata points to upstream ownership and generated live paths.

Required check: verify the installer output and then verify host-side discovery. Installer success is not enough.

### Command Or Workflow Pack

Shape: slash commands, planning files, hooks, prompt commands, or workflow folders are the real interface.

Default action: install those files into the target host's expected command or workflow location.

Local adaptation: create a small routing skill only when the host cannot discover the command pack directly.

Required check: run one positive command smoke and one near-miss smoke where the adapter should stay quiet.

### Runtime Or Workflow Engine

Shape: CLI, MCP server, web service, daemon, DAG executor, database-backed workflow system, or project-local workflow runtime.

Default action: install and verify the runtime as a runtime. Keep workflow definitions in the project that owns the process.

Local adaptation: a skill may describe when to call the runtime, but it must not pretend the runtime is a normal always-on `SKILL.md`.

Required check: verify binary or server health, workflow discovery, and at least one minimal workflow execution path.

## Adapter Contract

Every thin adapter should include:

- upstream name and URL or local canonical path
- pinned version, commit, tag, or explicit "floating latest" policy
- host surfaces that consume it
- invocation entrypoint
- refresh command or upstream update procedure
- generated paths or projections
- unsafe defaults that require explicit opt-in
- positive smoke and negative smoke

Keep adapter text short. Put long upstream methodology in the upstream project or a reference file, not in the adapter.

## Verification Ladder

Use the cheapest level that proves the live surface:

1. Structure check: `quick_validate` for local native skills or agents.
2. Link/projection check: `link_skill.py --status` or `link_agent.py --status`.
3. Installer receipt check: upstream installer output, generated files, and version pin.
4. Host discovery check: fresh host session or cache refresh confirms the asset is visible.
5. Behavior smoke: one positive route exercises the capability.
6. Boundary smoke: one near-miss proves the adapter does not over-trigger.

For cached hosts, do not claim completion until a fresh session or explicit rediscovery check sees the new surface.

## Unsafe Defaults

Avoid these:

- treating every external repository as a skill directory
- copying the same upstream files into every host as editable sources
- hand-maintaining parallel `SKILL.md` forks for the same capability
- silently enabling browser control, telemetry, auto-update, network tunnels, or team modes
- confusing installer success with live host discovery
- hiding generated projections inside the canonical source tree without marking them as generated

## Sidecar Activation

Treat method bundles, command packs, review suites, and workflow runtimes by
their actual asset shape rather than by a named local dispatcher. One primary
owner remains responsible for the requested result. A secondary capability is
activated through an explicit host surface and retains its upstream ownership.

Lifecycle work is complete when the install shape, upstream pin, refresh path,
host discovery, and declared smoke checks are proven. Project-truth acceptance
belongs to the repository's governance owner.

For a broad suite, choose the narrowest supported activation surface:

- passive cache outside the host discovery directory
- one thin explicit adapter with narrow trigger text
- command-only runtime invocation
- project-local workflow files activated only when the project adopts them
