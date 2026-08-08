#!/usr/bin/env python3
"""
Quick validation script for skills and agents.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from utils import parse_markdown_frontmatter


ALLOWED_NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
COMMON_ALLOWED_PROPERTIES = {"name", "description", "compatibility", "metadata"}
SKILL_ALLOWED_PROPERTIES = COMMON_ALLOWED_PROPERTIES | {
    "license",
    "allowed-tools",
    "disable-model-invocation",
}
AGENT_ALLOWED_PROPERTIES = COMMON_ALLOWED_PROPERTIES | {"tools"}


def parse_frontmatter(doc_path: Path):
    try:
        frontmatter, _ = parse_markdown_frontmatter(doc_path)
    except ValueError as exc:
        return False, str(exc), None

    return True, "ok", frontmatter


def validate_common_frontmatter(frontmatter, allowed_properties, doc_label):
    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in {doc_label} frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(allowed_properties))}"
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not ALLOWED_NAME_PATTERN.match(name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "ok"


def validate_skill(skill_path):
    """Basic validation of a skill."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    ok, message, frontmatter = parse_frontmatter(skill_md)
    if not ok:
        return False, message

    ok, message = validate_common_frontmatter(frontmatter, SKILL_ALLOWED_PROPERTIES, "SKILL.md")
    if not ok:
        return False, message

    invocation_flag = frontmatter.get("disable-model-invocation")
    if invocation_flag is not None and str(invocation_flag).lower() not in {"true", "false"}:
        return False, "'disable-model-invocation' must be true or false"

    return True, "Skill is valid!"


def validate_agent(agent_path):
    """Basic validation of an agent."""
    agent_path = Path(agent_path)
    agent_md = agent_path / "AGENT.md"
    if not agent_md.exists():
        return False, "AGENT.md not found"

    ok, message, frontmatter = parse_frontmatter(agent_md)
    if not ok:
        return False, message

    ok, message = validate_common_frontmatter(frontmatter, AGENT_ALLOWED_PROPERTIES, "AGENT.md")
    if not ok:
        return False, message

    body = agent_md.read_text().split("---", 2)[-1].strip()
    if not body:
        return False, "AGENT.md body cannot be empty"

    return True, "Agent is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.quick_validate <skill_or_agent_directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if (target / "SKILL.md").exists():
        valid, message = validate_skill(target)
    elif (target / "AGENT.md").exists():
        valid, message = validate_agent(target)
    else:
        valid, message = False, "Neither SKILL.md nor AGENT.md found"

    print(message)
    sys.exit(0 if valid else 1)
