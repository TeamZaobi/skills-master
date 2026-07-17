# Skill Layout Contract

Use this reference after the asset owner and intended consumers are known. The
layout records ownership; projections record host discovery.

## Asset Shapes

| Shape | Canonical path | Select when |
|---|---|---|
| `user_native` | `~/.agents/skills/<name>` | One user owns and installs the skill globally. |
| `project_native` | `<repo>/.agents/skills/<name>` | The skill exists only to operate inside one project. |
| `repo_product` | `<repo>/skills/<name>` | The repository owns, distributes, or projects the skill to multiple hosts. |
| `generated_product` | `<repo>/skills/src/<name>` with output under `skills/dist/` | A real reproducible build transforms source into the host-consumed asset. |

`repo_product` is the default for a repository-owned portable skill. A source
directory named `src` is evidence of a build boundary only when the registry
also declares the build command, output directory, and reproducibility check.

## Projection Contract

- A projection is read-only and points directly to the canonical directory.
- A host projection cannot target another host projection.
- Several hosts may share one discovery directory when they support it.
- A compatibility projection is explicit in the registry and removable after a
  fresh-session discovery check passes through the primary path.
- A real directory at a projection target is protected; linking requires a
  deliberate reconciliation rather than an overwrite.

## Path Contract

- Skill-internal Markdown links resolve relative to the file containing them.
- Repository-owned paths are expressed from the repository root in prose and
  machine manifests.
- A path that leaves the repository is an external dependency. Declare it in
  registry v2 and resolve it through that dependency instead of counting `..`
  path segments inside `SKILL.md`.
- An optional dependency being absent disables only its integration branch; the
  portable core remains valid.

## Generated Product Contract

A `generated_product` skill declares all of:

```toml
layout = "generated_product"
build_command = "..."
output_dir = "skills/dist/<name>"
reproducibility_check = "..."
```

The doctor rejects the layout when any field is missing or the output directory
escapes `skills/dist/`.
