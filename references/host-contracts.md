# Host Contracts

Use this reference before changing invocation metadata, discovery paths, or
link targets. Host facts drift; these mappings were verified against official
documentation on 2026-08-08. Recheck the relevant host before mutation.

## Invocation Mapping

Treat invocation as one semantic choice and render the host-specific controls:

| Intent | Codex | Claude Code | Kimi Code CLI |
|---|---|---|---|
| Model may invoke | Omit `policy.allow_implicit_invocation` or set it to `true` in `agents/openai.yaml` | Omit `disable-model-invocation` or set it to `false` | Omit `disableModelInvocation` or set it to `false` |
| Explicit user invocation only | Set `policy.allow_implicit_invocation: false` in `agents/openai.yaml` | Set `disable-model-invocation: true` in `SKILL.md` | Set `disableModelInvocation: true`; the kebab-case alias is accepted |

A portable user-invoked source may therefore carry both the kebab-case
frontmatter field and the Codex policy file. They are host renderings of one
decision, not independent editable policy.

Sources:

- [Codex skills](https://developers.openai.com/codex/skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Kimi Code Agent Skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html)

## Discovery Paths

### Codex

- User: `~/.agents/skills`
- Repository: `.agents/skills` from the working directory through repository
  ancestors
- Admin: `/etc/codex/skills`
- Bundled system skills: host-managed

Codex follows symlinked Skill directories. `~/.codex/skills` is not a current
documented authoring location; retain an existing entry only as an explicitly
declared local compatibility surface.

### Claude Code

- User: `~/.claude/skills`
- Project: `.claude/skills`
- Plugin: `<plugin>/skills`

Claude Code follows symlinked Skill directories. It watches existing Skill
directories for `SKILL.md` changes; creating a new top-level discovery
directory may still require restart.

### Kimi Code CLI

- User: `$KIMI_CODE_HOME/skills` (normally `~/.kimi-code/skills`) and
  `~/.agents/skills`
- Project: `.kimi-code/skills` and `.agents/skills`
- Extra: `extra_skill_dirs` in `config.toml`

Kimi documents scope precedence as Project, User, Extra, then Built-in. The
official page does not declare precedence between the two directories inside a
single scope, so duplicate same-name sources require live verification rather
than a hard-coded winner.

### Google Antigravity

- Project/workspace: `.agents/skills`
- User/global: `~/.gemini/config/skills`

Google's current codelab distinguishes Antigravity product variants and warns
that paths are time-bound. Treat any Antigravity CLI-specific user path as a
deployment setting verified against the installed product, not as a portable
default.

Source: [Authoring Google Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)

## Companion Agents

Companion-agent formats are host-specific derived artifacts:

- Codex personal agents are standalone TOML files in `~/.codex/agents/`;
  project agents use `.codex/agents/`. Each requires `name`, `description`, and
  `developer_instructions`.
- Claude Code personal agents are Markdown files in `~/.claude/agents/`;
  project agents use `.claude/agents/`. `name` and `description` are required,
  and the Markdown body is the system prompt.

Keep `AGENT.md` as a lifecycle-owned canonical interchange source only when the
registry or repository declares that design. `scripts/link_agent.py` renders
the current Codex TOML and links the Claude Markdown body; reverify both host
schemas before extending the renderer.

Sources:

- [Codex subagents](https://developers.openai.com/codex/multi-agent)
- [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents)

## Completion Criterion

The mapping is complete when every declared host has a current official or
installed-instance source, the canonical intent is rendered once per host, and
a fresh host check confirms both visibility and invocation behavior.
