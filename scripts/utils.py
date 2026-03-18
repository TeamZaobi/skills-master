"""Shared utilities for skills-master scripts."""

from pathlib import Path


def parse_markdown_frontmatter(doc_path: Path) -> tuple[dict[str, str], str]:
    """Parse a markdown file with YAML frontmatter and return (metadata, body)."""
    content = doc_path.read_text()
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{doc_path.name} missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"{doc_path.name} missing frontmatter (no closing ---)")

    metadata: dict[str, str] = {}
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if ":" not in line:
            i += 1
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in (">", "|", ">-", "|-"):
            continuation_lines: list[str] = []
            i += 1
            while i < len(frontmatter_lines) and (
                frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")
            ):
                continuation_lines.append(frontmatter_lines[i].strip())
                i += 1
            metadata[key] = " ".join(continuation_lines)
            continue

        metadata[key] = value.strip('"').strip("'")
        i += 1

    body = "\n".join(lines[end_idx + 1 :]).strip()
    return metadata, body


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text()
    metadata, _ = parse_markdown_frontmatter(skill_md)
    return metadata.get("name", ""), metadata.get("description", ""), content


def parse_agent_md(agent_path: Path) -> tuple[str, str, str]:
    """Parse an AGENT.md file, returning (name, description, full_content)."""
    agent_md = agent_path / "AGENT.md"
    content = agent_md.read_text()
    metadata, _ = parse_markdown_frontmatter(agent_md)
    return metadata.get("name", ""), metadata.get("description", ""), content
