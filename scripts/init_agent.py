#!/usr/bin/env python3
"""
Agent Initializer - Creates a new canonical agent from template

Usage:
    init_agent.py <agent-name> [--path <path>] [--project-root <path>] [--link | --no-link]
"""

import argparse
import re
import sys
from pathlib import Path

MAX_AGENT_NAME_LENGTH = 64
RESERVED_NAME_TOKENS = {"anthropic", "claude", "codex", "agent", "ai"}
DEFAULT_GLOBAL_HUB = (Path.home() / ".agents" / "agents").resolve()


AGENT_TEMPLATE = """---
name: {agent_name}
description: [TODO: Complete and informative explanation of what this agent owns and when to invoke it.]
---

# {agent_title}

## Mission

[TODO: State the perspective this agent owns.]

## Responsibilities

- [TODO: What this agent should do]
- [TODO: What this agent should not do]

## Boundaries

- [TODO: Explicitly state where this agent must stop]

## Tooling Notes

- [TODO: If this agent should trigger skills or downstream workers, describe the boundary here.]
"""


def title_case_agent_name(agent_name):
    return " ".join(word.capitalize() for word in agent_name.split("-"))


def validate_agent_name(agent_name):
    if not re.match(r"^[a-z0-9-]+$", agent_name):
        return False, "Agent name must be hyphen-case (lowercase letters, digits, hyphens only)."
    if agent_name.startswith("-") or agent_name.endswith("-") or "--" in agent_name:
        return False, "Agent name cannot start/end with hyphen or contain consecutive hyphens."
    if len(agent_name) > MAX_AGENT_NAME_LENGTH:
        return False, (
            f"Agent name is too long ({len(agent_name)} chars). "
            f"Maximum is {MAX_AGENT_NAME_LENGTH}."
        )
    reserved_hits = sorted({token for token in agent_name.split("-") if token in RESERVED_NAME_TOKENS})
    if reserved_hits:
        return False, (
            f"Agent name contains reserved token(s): {', '.join(reserved_hits)}. "
            "Use a neutral name."
        )
    return True, None


def init_agent(agent_name, path):
    agent_dir = Path(path).resolve() / agent_name
    if agent_dir.exists():
        print(f"❌ Error: Agent directory already exists: {agent_dir}")
        return None

    try:
        agent_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created agent directory: {agent_dir}")
    except Exception as exc:
        print(f"❌ Error creating directory: {exc}")
        return None

    agent_title = title_case_agent_name(agent_name)
    agent_md_path = agent_dir / "AGENT.md"
    try:
        agent_md_path.write_text(
            AGENT_TEMPLATE.format(agent_name=agent_name, agent_title=agent_title)
        )
        print("✅ Created AGENT.md")
    except Exception as exc:
        print(f"❌ Error creating AGENT.md: {exc}")
        return None

    print(f"\n✅ Agent '{agent_name}' initialized successfully at {agent_dir}")
    print("\nNext steps:")
    print("1. Edit AGENT.md to complete the TODO items and tighten the boundaries")
    print("2. Run the validator when ready to check the agent structure")
    return agent_dir


def is_global_hub(path):
    resolved = Path(path).expanduser().resolve()
    return resolved == DEFAULT_GLOBAL_HUB


def default_project_hub(project_root):
    return Path(project_root).expanduser().resolve() / ".agents" / "agents"


def is_project_hub(path, project_root):
    if project_root is None:
        return False
    return Path(path).expanduser().resolve() == default_project_hub(project_root)


def auto_link(agent_dir, project_root=None):
    sys.path.insert(0, str(Path(__file__).parent))
    from link_agent import link_agent, resolve_agent_path

    agent_path = resolve_agent_path(str(agent_dir))
    if agent_path is None:
        print("⚠  Could not project agent (invalid path)")
        return

    print("\n🔗 Projecting to development tools...")
    created, updated, skipped, warnings = link_agent(agent_path, project_root=project_root)
    print(f"   Done: {created} created, {updated} updated, {skipped} skipped, {warnings} warnings")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new canonical agent from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s review-agent --path ~/.agents/agents
  %(prog)s review-agent --path ~/.agents/agents --no-link
  %(prog)s review-agent --project-root /path/to/repo
        """,
    )
    parser.add_argument("agent_name", help="Name of the agent (hyphen-case)")
    parser.add_argument(
        "--path",
        help="Directory where the agent folder will be created (default: ~/.agents/agents or <project-root>/.agents/agents)",
    )
    parser.add_argument(
        "--project-root",
        help="Project root for project-scoped agents; default shared hub is <project-root>/.agents/agents",
    )

    link_group = parser.add_mutually_exclusive_group()
    link_group.add_argument("--link", action="store_true", default=None, help="Project to default tool directories after creation")
    link_group.add_argument("--no-link", action="store_true", default=False, help="Skip auto-projection even for the global hub")

    args = parser.parse_args()
    agent_name = args.agent_name.strip()
    if not agent_name:
        print("❌ Error: Agent name cannot be empty.")
        sys.exit(1)
    valid, error_message = validate_agent_name(agent_name)
    if not valid:
        print(f"❌ Error: {error_message}")
        sys.exit(1)

    target_path = args.path
    if target_path is None:
        target_path = (
            str(default_project_hub(args.project_root))
            if args.project_root
            else str(DEFAULT_GLOBAL_HUB)
        )

    print(f"🚀 Initializing agent: {agent_name}")
    print(f"   Location: {target_path}")
    if args.project_root:
        print(f"   Project root: {Path(args.project_root).expanduser().resolve()}")
    print()

    result = init_agent(agent_name, target_path)

    if result:
        should_link = args.link
        if should_link is None and not args.no_link:
            should_link = is_global_hub(target_path) or is_project_hub(target_path, args.project_root)

        if should_link:
            auto_link(result, project_root=args.project_root)

        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
