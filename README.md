# Skills Master

`skills-master` governs the lifecycle of skills and companion agents: creation,
maintenance, upstream convergence, evaluation, installation, projection,
packaging, and discovery diagnosis.

The repository keeps the agent entrypoint compact and moves conditional detail
into references and deterministic work into scripts.

## Start Here

- Agent operating instructions: [SKILL.md](SKILL.md)
- Canonical layout choices: [references/layout-contract.md](references/layout-contract.md)
- Registry v2: [references/registry-v2.md](references/registry-v2.md)
- Multi-host adaptation: [references/multi-tool-adaptation.md](references/multi-tool-adaptation.md)
- Content placement: [references/structure-boundaries.md](references/structure-boundaries.md)

## Common Commands

```bash
# Create a repository-owned distributable skill.
python3 scripts/init_skill.py my-skill --layout repo-product --project-root /path/to/repo

# Validate one standalone asset.
python3 -m scripts.quick_validate /path/to/repo/skills/my-skill

# Validate repository topology when the repository declares skills/registry.toml.
python3 scripts/doctor.py /path/to/repo

# Inspect or refresh direct host projections.
python3 scripts/link_skill.py /path/to/repo/skills/my-skill --project-root /path/to/repo --status

# Package after validation.
python3 -m scripts.package_skill /path/to/repo/skills/my-skill ./dist
```

## Repository Map

- `scripts/`: initialization, validation, linking, packaging, evaluation, and doctor tooling
- `references/`: layout, host, workflow, schema, and boundary contracts
- `evals/`: trigger and ownership boundary cases
- `agents/`: optional comparison, grading, and analysis roles
- `eval-viewer/`: human review rendering

Python 3.9+ is supported. Registry v2 uses the standard `tomllib` when available
and a bundled parser for its deterministic subset on Python 3.9-3.10.

Current release details are in [VERSION.md](VERSION.md).
