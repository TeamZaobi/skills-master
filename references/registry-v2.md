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
```

## Required Fields

- Root: `version`, `layout`, `canonical_dir`
- Projection: `id`, `path`, `hosts`; `required` defaults to `true`
- Skill: `name`, `source`; `layout` may override the root layout; `targets`
  defaults to all required projections
- Dependency: `id`, `root_hint`, `required`, `role`

Generated products additionally require `build_command`, `output_dir`, and
`reproducibility_check` on the skill entry.

## Migration From v1

1. Classify each registered skill using the layout contract.
2. Move repository products from `skills/src/<name>` to `skills/<name>`.
3. Change every active consumer to the new canonical path.
4. Replace projection chains with direct links.
5. Register every external repository dependency.
6. Run `scripts/doctor.py`; remove the old directory only after it reports no
   active canonical or projection dependency on that path.

Historical receipts and immutable snapshots keep their original path text.
They describe the environment in which they were produced and are not live
consumers.

