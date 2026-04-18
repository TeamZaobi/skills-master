# Workflow Patterns

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give the model an overview of the process near the beginning of `SKILL.md`:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Conditional Workflows

For tasks with branching logic, guide the model through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## A/B E2E Workflows

For skill modifications, upgrades, capability additions, or boundary rewrites, a controlled A/B E2E workflow is often more reliable than a one-off trial.

Example:

```markdown
To check whether the new skill draft is actually better:

1. Freeze the prompt set and scoring rubric
2. Define the two conditions:
   `with_skill` vs `without_skill`, or `new_skill` vs `old_skill`
3. Spawn a fresh isolated worker for every run
4. Run every prompt under every condition three times
5. Keep the model, files, response cap, and output contract identical
6. Grade each run separately
7. Aggregate per prompt and per condition
8. Inspect deltas and regressions before editing again
```

If the environment does not support subagents, simulate isolation with fresh serial sessions. Do not reuse the same conversation state across conditions when the goal is to measure prompt value.
