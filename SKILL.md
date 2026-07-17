---
name: skills-master
description: Skill lifecycle. Use when creating, changing, syncing, evaluating, packaging, installing, projecting, or diagnosing discovery of a skill or companion agent.
---

# Skills Master

Make skill and companion-agent lifecycle changes predictable. Use one editable
source, make the smallest justified change, and prove that every declared host
consumes the intended asset.

## 1. Classify The Asset Shape

Identify the owner, scope, distribution needs, and whether a reproducible build
really exists. Select exactly one shape:

- `user_native`
- `project_native`
- `repo_product`
- `generated_product`

Read [`references/layout-contract.md`](references/layout-contract.md) when the
canonical location is not already explicit.

Completion criterion: one shape is selected and its canonical path satisfies
the layout contract.

## 2. Pin The Source And Consumers

Inspect the live asset, editable source, meaningful upstream, local divergence,
host discovery paths, packages, and projections. Classify every similar copy as
canonical, upstream, projection, generated output, package, cache, or stale
material.

For multi-host or registry-backed work, read
[`references/multi-tool-adaptation.md`](references/multi-tool-adaptation.md) and
[`references/registry-v2.md`](references/registry-v2.md).

Completion criterion: every editable copy and live consumer is accounted for,
and exactly one editable source remains.

## 3. Make The Smallest Lifecycle Change

Edit the canonical source only. Preserve local adaptations when comparing with
upstream. Keep core execution in `SKILL.md` or `AGENT.md`; place conditional
detail in `references/`, deterministic mechanics in `scripts/`, reusable output
material in `assets/`, and benchmark inputs in `evals/`.

Use the provided initializer, linker, validator, packager, and doctor instead of
hand-maintaining parallel copies. Route project truth, runtime behavior, product
requirements, and domain decisions to their existing owners.

Completion criterion: the requested behavior changed at the canonical source,
with no new editable twin and no projection-to-projection chain.

## 4. Prove Discovery And Behavior

Use the cheapest proof that covers the change:

```bash
python3 -m scripts.quick_validate <skill-or-agent-path>
python3 scripts/link_skill.py <skill-path> --status
python3 -m scripts.package_skill <skill-path>
# Registry-backed repositories only:
python3 scripts/doctor.py <project-root>
```

Open a fresh host session when discovery is cached. Add a positive smoke and a
near-miss smoke when triggers, ownership, or behavior boundaries changed. Use a
controlled A/B comparison for prompt-sensitive or high-risk changes.

Completion criterion: every declared host resolves to the same canonical
realpath, structural checks pass, and the positive plus near-miss behavior stays
inside the intended boundary.

## Conditional References

- Existing-asset maintenance and upstream convergence:
  [`references/workflows.md`](references/workflows.md)
- Fleet-wide inventory, owner/disposition tracking, and cleanup waves:
  [`references/fleet-policy.v1.toml`](references/fleet-policy.v1.toml) with
  `scripts/fleet_scan.py`
- Skill/agent content placement:
  [`references/structure-boundaries.md`](references/structure-boundaries.md)
- Multi-skill ownership and handoff:
  [`references/multi-skill-strategy.md`](references/multi-skill-strategy.md)
- External method-skill adaptation, including TDD / BDD:
  [`references/multi-tool-adaptation.md`](references/multi-tool-adaptation.md)
- Evaluation schemas and outputs:
  [`references/schemas.md`](references/schemas.md) and
  [`references/output-patterns.md`](references/output-patterns.md)
