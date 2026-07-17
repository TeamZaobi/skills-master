# Skill Registry v2

Registry v2 makes canonical ownership, host projections, and external
dependencies machine-checkable.

## Minimal Repository Product Registry

```toml
version = 2
layout = "repo_product"
canonical_dir = "skills"

[[projection]]
id = "agents"
path = ".agents/skills"
hosts = ["codex", "gemini"]
required = true

[[projection]]
id = "claude"
path = ".claude/skills"
hosts = ["claude"]
required = true

[[skill]]
name = "example"
source = "skills/example"
status = "active"
targets = ["agents", "claude"]

[[dependency]]
id = "optional-sibling"
root_hint = "../OptionalSibling"
required = false
role = "integration_only"

[[consumer_skill]]
name = "external-example"
dependency = "optional-sibling"
source = "skills/external-example"
targets = ["agents", "claude"]
```

## Required Fields

- Root: `version`, `layout`, `canonical_dir`
- Projection: `id`, `path`, `hosts`; `required` defaults to `true`
- Skill: `name`, `source`; `layout` may override the root layout; `targets`
  defaults to all required projections
- Dependency: `id`, `root_hint`, `required`, `role`
- Consumer Skill: `name`, `dependency`, `source`, `targets`. `source` is
  relative to the dependency root. A consumer entry creates discovery
  projections only; it is not a fifth canonical asset shape and grants no
  write authority to the consuming repository.

A sidecar installed directly from an upstream package remains installer-owned.
When a repository deliberately forks one, declare the canonical source instead:

```toml
[[sidecar]]
name = "example-sidecar"
upstream = "owner/repository"
source_mode = "project_local_fork"
source_path = "vendor/skill-forks/owner-repository/example-sidecar"
upstream_commit = "0123456789abcdef0123456789abcdef01234567"
```

`source_path` must stay inside the declaring repository and contain
`SKILL.md`. Registry-driven fleet discovery treats that directory as a
repo-owned audit source even when every host entry is a symlink. The registry,
lock receipt, upstream commit, fork digest, projection, license, and rollback
point must agree before adoption; the fork does not inherit authority over
project facts merely because it is repository-owned.

Generated products additionally require `build_command`, `output_dir`, and
`reproducibility_check` on the skill entry.

## Host Coverage

Kimi Code natively discovers project skills from `.agents/skills`, so the
shared `agents` projection already serves it; add `"kimi"` to that
projection's `hosts` when the repository officially supports Kimi Code.

Declare a separate opt-in projection only for Kimi-only skills or
Kimi-specific variants:

```toml
[[projection]]
id = "kimi"
path = ".kimi-code/skills"
hosts = ["kimi"]
required = false
```

When one name is visible from both project discovery directories, Kimi Code
loads it from `.kimi-code/skills` first. The doctor reports
`projection_kimi_shadow` when the two copies resolve to different realpaths,
because the hosts would otherwise see different content.

## Migration From v1

1. Classify each registered skill using the layout contract.
2. Move repository products from `skills/src/<name>` to `skills/<name>`.
3. Change every active consumer to the new canonical path.
4. Replace projection chains with direct links.
5. Register every external repository dependency.
6. When a repository consumes an external Skill, register it as
   `[[consumer_skill]]` and project every host directly to the dependency's
   canonical source. Do not keep a local editable mirror.
7. Run `scripts/doctor.py`; remove the old directory only after it reports no
   active canonical or projection dependency on that path.

Historical receipts and immutable snapshots keep their original path text.
They describe the environment in which they were produced and are not live
consumers.
