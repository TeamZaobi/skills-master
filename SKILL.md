---
name: skills-master
description: Skill lifecycle. Use when locating the canonical source, reconciling upstream or duplicate copies, installing, linking, packaging, distributing, or diagnosing host discovery of a skill or companion agent.
---

# Skills Master

Own the asset lifecycle: ownership, source, consumers, distribution, and live
discovery. `writing-for-agents` owns agent-facing wording, information
hierarchy, completion criteria, and invocation design. For mixed work, apply
that writing contract to the content, then return here to prove the intended
source reaches each declared consumer.

## Step 1: Bind Ownership

Identify the owner, scope, consumers, and distribution boundary. Select one
canonical ownership shape for each editable asset:

- `user_native`
- `project_native`
- `repo_product`
- `generated_product`

Read [`references/layout-contract.md`](references/layout-contract.md) when the
canonical location is not already explicit.

Completion criterion: every editable asset has one named owner, one ownership
shape, and a canonical path that satisfies the layout contract.

## Step 2: Pin Sources And Consumers

Inspect the live asset, editable source, meaningful upstream, local divergence,
host discovery paths, packages, adapters, and projections. Classify every
similar copy as canonical source, upstream, read-only projection, generated
output, adapter, package, cache, or stale material.

For registry-backed work, read
[`references/registry-v2.md`](references/registry-v2.md). For multi-host or
external bundles, read
[`references/multi-tool-adaptation.md`](references/multi-tool-adaptation.md).

Completion criterion: every editable copy and live consumer is accounted for,
and each owner scope has exactly one editable source.

## Step 3: Change The Lifecycle Surface

Edit the canonical source or its declared build/config owner. Preserve local
adaptations when comparing with upstream. Use the initializer only to create a
minimal source; add scripts, references, assets, evals, adapters, or generated
outputs only when a real branch needs them.

Invocation is one semantic choice with host-specific representations. Read
[`references/host-contracts.md`](references/host-contracts.md) before changing
frontmatter, `agents/openai.yaml`, discovery paths, or link targets.

Use the provided linker, validator, packager, and doctor for the mechanics they
actually cover. Keep project truth, runtime behavior, product requirements, and
domain decisions with their existing owners.

Completion criterion: the requested lifecycle behavior changed at its owner,
with no new editable twin, hidden host fork, or projection-to-projection chain.

## Step 4: Prove The Declared Consumers

Use the cheapest proof that covers the changed surface:

```bash
python3 -m scripts.quick_validate <skill-or-agent-path>
python3 scripts/link_skill.py <skill-path> --status
python3 -m scripts.package_skill <skill-path>
# Registry-backed repositories only:
python3 scripts/doctor.py <project-root>
```

Use a fresh session or the host's documented reload behavior when discovery is
cached. Discovery proof covers visibility and invocation policy; the owner of
the changed agent-facing behavior supplies its positive and near-miss behavior
proof.

Completion criterion: every declared host resolves to the intended canonical
source or declared derived artifact, structural checks pass, and fresh host
evidence confirms the intended discovery and invocation boundary.

## Conditional References

- Existing-asset maintenance and upstream convergence:
  [`references/workflows.md`](references/workflows.md)
- Current host discovery and invocation mappings:
  [`references/host-contracts.md`](references/host-contracts.md)
- Multi-skill ownership and handoff:
  [`references/multi-skill-strategy.md`](references/multi-skill-strategy.md)
- Fleet inventory: copy
  [`references/fleet-policy.example.toml`](references/fleet-policy.example.toml)
  to an explicit deployment config, then pass it with `--policy`. Use
  `scripts/content_audit.py` only for objective static signals; semantic writing
  quality remains rubric-guided review.
- Retained evaluation receipt schemas:
  [`references/schemas.md`](references/schemas.md)
