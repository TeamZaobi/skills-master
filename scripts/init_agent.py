#!/usr/bin/env python3
"""Create a minimal canonical companion-agent source."""

import argparse
import re
import sys
from pathlib import Path


MAX_AGENT_NAME_LENGTH = 64
DEFAULT_GLOBAL_HUB = (Path.home() / ".agents" / "agents").resolve()

AGENT_TEMPLATE = """---
name: {agent_name}
description: "[TODO: State the distinct job this agent owns and when a host should delegate to it.]"
---

# {agent_title}

[TODO: Write the agent-facing contract. Keep the job narrow, declare its
authority and completion criterion, and add host-specific capabilities only
when the target host supports them.]
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
    return True, None


def init_agent(agent_name, path):
    """Create one minimal AGENT.md source and return its directory."""
    agent_dir = Path(path).expanduser().resolve() / agent_name
    if agent_dir.exists():
        print(f"❌ Error: Agent directory already exists: {agent_dir}")
        return None

    try:
        agent_dir.mkdir(parents=True, exist_ok=False)
        (agent_dir / "AGENT.md").write_text(
            AGENT_TEMPLATE.format(
                agent_name=agent_name,
                agent_title=title_case_agent_name(agent_name),
            ),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"❌ Error creating companion agent: {exc}")
        return None

    print(f"✅ Created minimal companion-agent source: {agent_dir}")
    print("Next: replace the TODOs, add only supported host capabilities, then run quick_validate.")
    return agent_dir


def default_project_hub(project_root):
    return Path(project_root).expanduser().resolve() / ".agents" / "agents"


def auto_link(agent_dir, project_root=None):
    """Project a new source only after explicit --link authorization."""
    sys.path.insert(0, str(Path(__file__).parent))
    from link_agent import link_agent, resolve_agent_path

    agent_path = resolve_agent_path(str(agent_dir))
    if agent_path is None:
        print("⚠  Could not project companion agent (invalid path)")
        return
    created, updated, skipped, warnings = link_agent(agent_path, project_root=project_root)
    print(f"Done: {created} created, {updated} updated, {skipped} skipped, {warnings} warnings")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a minimal canonical companion-agent source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s code-reviewer --path ~/.agents/agents
  %(prog)s repo-reviewer --project-root /path/to/repo
  %(prog)s repo-reviewer --project-root /path/to/repo --link
        """,
    )
    parser.add_argument("agent_name", help="Hyphen-case companion-agent name")
    parser.add_argument("--path", help="Canonical parent directory")
    parser.add_argument("--project-root", help="Project root for a project-owned source")
    parser.add_argument(
        "--link",
        action="store_true",
        help="After creation, project to the configured default hosts",
    )
    args = parser.parse_args()

    agent_name = args.agent_name.strip()
    valid, error_message = validate_agent_name(agent_name)
    if not valid:
        parser.error(error_message)

    target_path = args.path or (
        str(default_project_hub(args.project_root))
        if args.project_root
        else str(DEFAULT_GLOBAL_HUB)
    )
    result = init_agent(agent_name, target_path)
    if result is None:
        return 1
    if args.link:
        auto_link(result, project_root=args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
