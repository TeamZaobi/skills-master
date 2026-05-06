# Skill Structure Boundaries

Use this note when a skill has received several direct `SKILL.md` edits and the
next change may turn the main entry into a patch log.

## Keep In SKILL.md

Keep content in `SKILL.md` when it is part of the always-loaded execution path:

- trigger and routing conditions
- first decision or preflight steps
- source-of-truth and live-path rules
- hard safety constraints
- validation steps the agent must run before finishing
- short rules that prevent repeated user corrections

Prefer direct `SKILL.md` edits for small companion skills where the whole asset is
the live operating surface.

## Move To References

Move content into `references/` when it is useful but not always needed:

- provider or backend matrices
- host-specific inventories
- long community practice digests
- official-doc research summaries
- case histories and receipts
- variant workflows for one platform
- examples that explain a rule but are not themselves the rule

The main skill should link to the reference with a short load condition, not copy
the full detail back into the body.

## Move To Scripts Or Data

Use `scripts/` or structured data when the text describes repeatable mechanics:

- link or projection refresh logic
- config inspection or redaction
- validation and smoke checks
- benchmark aggregation
- route registries, model registries, or tool manifests

Do not preserve a hand-written checklist when a script can make the check
deterministic.

## Rewrite Instead Of Append

When the same section has been patched more than twice for the same concept,
rewrite the section around the current truth:

1. identify the claim that changed;
2. delete stale wording and duplicate exceptions;
3. keep the short current rule in `SKILL.md`;
4. move history, examples, and edge cases to a reference file;
5. validate that the live consumer path still loads the intended skill.

Completion means the skill is easier to load and follow than before, not merely
that the latest lesson was appended.
