# Lifecycle Workflows

Use these branches after ownership and the canonical path are bound. Content
design, instruction hierarchy, and invocation semantics follow
`writing-for-agents`; these workflows prove source convergence and delivery.

## Existing Asset And Upstream

1. Record the canonical source, live consumers, upstream URL, and current pins.
2. Compare upstream, canonical source, packages, and live projections without
   editing any derived copy.
3. Classify each difference as upstream change, owned local adaptation,
   generated output, stale projection, or unresolved conflict.
4. Apply the accepted delta at its owner and regenerate declared derivatives.
5. Validate structure, direct projections, package contents, and fresh-host
   discovery for the changed consumers.

Completion criterion: each accepted delta has one owner, local adaptations are
preserved or deliberately retired, and every declared consumer resolves to the
accepted source or generated artifact.

## New Lifecycle Surface

1. Obtain the agent-facing contract from `writing-for-agents`, including
   invocation mode and explicit completion criteria.
2. Select `user_native`, `project_native`, `repo_product`, or
   `generated_product` ownership.
3. Run `scripts/init_skill.py` only when a new minimal source is needed.
4. Add conditional resources when the contract has a real branch that needs
   them.
5. Project, package, and verify only the declared consumers.

Completion criterion: the minimal canonical source exists at the selected
owner, invocation policy is rendered for each declared host, and all declared
consumers pass the appropriate discovery check.

## Discovery Repair

1. Enumerate the host's currently documented discovery roots.
2. Resolve every same-name entry to its realpath and classify compatibility
   paths explicitly.
3. Reconcile editable twins before linking; preserve real directories until
   their ownership is decided.
4. Create direct projections from each host surface to the canonical source.
5. Check link status, then open a fresh session or use documented reload
   behavior.

Completion criterion: there is one editable source per owner scope, no
projection chain or ambiguous same-name conflict remains, and fresh-host
evidence identifies the intended asset.

## Fleet Audit

1. Copy `fleet-policy.example.toml` to a deployment-owned local policy.
2. Replace every sample root, owner, rubric, host, and tier with verified local
   truth.
3. Run the read-only scan with explicit `--policy` and preserve the finding
   ledger between cycles.
4. Review ownership decisions before any migration, relink, retirement, or
   deletion task is authorized separately.

Completion criterion: the run records its exact policy, roots, rubric, and
findings without mutating fleet assets.
