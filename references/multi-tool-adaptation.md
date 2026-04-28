# Multi-Tool Adaptation

Use this reference when a skill or agent lifecycle task involves more than one host tool, or when an upstream project is not a single native `SKILL.md` directory.

## Goal

Keep one canonical owner for the external capability while making each host consume the smallest compatible surface.

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

If the tool changes project truth, write boundaries, process state, recovery, or audit, hand the governance decision to `files-driven` before treating the adapter as accepted.

## Skill And Plugin Catalog

Do not treat the current four `Driven` sidecars as the whole tool universe.
Any discovered or candidate skill, plugin, connector, app, MCP surface, CLI, command pack, workflow runtime, or browser adapter can enter this intake path.

For an existing host-discovered skill:

- If the user's task simply matches the skill, use the skill normally.
- If the work changes trigger text, install location, upstream pin, generated projection, host discovery, or distribution, treat it as lifecycle work here.
- If the skill's output becomes project truth, write authority, process state, recovery evidence, or audit material, hand acceptance to `files-driven`.
- If the skill depends on an external ecosystem, check official manuals, installed examples, and mature community practice before writing a custom adapter.

## Asset Shapes

### Native Skill

Shape: one directory whose main contract is `SKILL.md`.

Default action: keep one editable source, then use `scripts/link_skill.py` for supported hosts.

Required check: run `link_skill.py <path> --status`, then open a fresh host session if the host caches discovery.

### Native Companion Agent

Shape: one directory whose main contract is `AGENT.md`.

Default action: keep one editable source, then use `scripts/link_agent.py` or the host's official agent projection.

Required check: run `link_agent.py <path> --status`, then verify that the target host can see the rendered agent.

### Multi-Skill Or Plugin Bundle

Shape: one upstream repository contains multiple skills, host plugin metadata, commands, hooks, or scripts.

Default action: use the upstream installer or host plugin mechanism. Do not symlink the repository root as if it were one skill.

Local adaptation: add a thin adapter only if the host needs a single trigger surface. The adapter should point to upstream ownership and list the generated live paths.

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

## Current Sidecar Pattern

For the Superpowers, GSD, gstack, and Archon family of external workflow tools:

- Treat the four together as the current `Driven` execution layer for `files-driven`: execution discipline, long-task drive, virtual-team challenge, and workflow orchestration.
- For Codex, keep broad `Driven` suites passive by default. Installing an upstream bundle is not permission to expose every generated skill on the default discovery path.
- Superpowers-style discipline plugins are sidecar methodology bundles. Prefer upstream install and host discovery verification; make MyWay or another dispatcher route to them instead of vendoring the whole method text.
- GSD-style command packs are long-context execution surfaces. Preserve their command or planning state model; adapt via trigger and invocation instructions.
- gstack-style virtual-team suites are selected secondary-review surfaces. Keep browser, telemetry, auto-update, and team/network features explicit opt-in.
- Archon-style systems are workflow runtimes. Install and verify the runtime and project workflow files; do not flatten the runtime into a normal skill.

The common rule is one primary owner per turn. Sidecars can be invoked deliberately, but they should not all activate by default.

Lifecycle work stops at proving install, adapter shape, upstream pin, refresh path, and live discovery. When a sidecar result needs to enter project truth, write boundaries, process state, recovery, or audit, hand off to `files-driven`; do not let the adapter or installer become the project governance owner.

If a host's skill discovery would make a broad suite too eager, prefer one of
these safer surfaces:

- passive cache outside the host discovery directory
- one thin explicit adapter with narrow trigger text
- command-only runtime invocation
- project-local workflow files activated only when the project adopts them
