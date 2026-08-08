# Skills Master

`skills-master` governs lifecycle state for skills and companion agents:
canonical ownership, upstream convergence, installation, projection,
packaging, distribution, and live discovery.

Agent-facing wording, instruction hierarchy, completion criteria, and
invocation design belong to `writing-for-agents`. This repository applies that
contract, then proves that the intended source reaches its declared hosts.

## Start Here

- Agent entrypoint: [SKILL.md](SKILL.md)
- Canonical layouts: [references/layout-contract.md](references/layout-contract.md)
- Dated host mappings: [references/host-contracts.md](references/host-contracts.md)
- Registry v2: [references/registry-v2.md](references/registry-v2.md)
- Lifecycle branches: [references/workflows.md](references/workflows.md)
- Multi-host adaptation: [references/multi-tool-adaptation.md](references/multi-tool-adaptation.md)

## Common Commands

```bash
# Create only the minimal lifecycle source after its writing contract is known.
python3 scripts/init_skill.py my-skill --layout repo-product \
  --project-root /path/to/repo --invocation user

# Create a minimal canonical companion-agent source without auto-projecting it.
python3 scripts/init_agent.py code-reviewer --project-root /path/to/repo

# Validate one standalone asset.
python3 -m scripts.quick_validate /path/to/repo/skills/my-skill

# Validate a registry-backed repository topology.
python3 scripts/doctor.py /path/to/repo

# Inspect or refresh direct host projections.
python3 scripts/link_skill.py /path/to/repo/skills/my-skill \
  --project-root /path/to/repo --status

# Package after validation.
python3 -m scripts.package_skill /path/to/repo/skills/my-skill ./dist

# Run a read-only fleet scan with an explicit deployment policy.
python3 scripts/fleet_scan.py --policy config/fleet-policy.local.toml \
  --output-dir /path/to/run/fleet \
  --previous-ledger /path/to/prior/finding-ledger.v1.json
```

## Repository Map

- `scripts/`: lifecycle initialization, validation, linking, packaging, fleet scanning, and topology checks
- `references/`: layout, host, workflow, registry, schema, and ownership contracts
- `evals/`: trigger and adjacent-owner boundary cases
- `agents/`: host-specific policy and display metadata

Python 3.9+ is supported. Deployment-specific fleet policies use ignored
`config/*.local.toml` files and are never packaged. Release details are in
[VERSION.md](VERSION.md).
