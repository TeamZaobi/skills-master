#!/usr/bin/env python3
"""
Skill Linker - Manage symlinks for multi-tool skill discovery

Creates/queries/removes symbolic links from a skill's source directory
to the skills directories of confirmed development tools.

Usage:
    link_skill.py <skill-path>                        # Link to default user-level targets
    link_skill.py <skill-path> --project-root <path> # Link into project tool dirs
    link_skill.py <skill-path> --targets claude,codex,antigravity # Link to specific targets
    link_skill.py <skill-path> --status               # Show link status
    link_skill.py <skill-path> --unlink               # Remove all links
    link_skill.py <skill-path> --unlink --targets codex  # Remove specific links
    link_skill.py <skill-path> --force                # Overwrite existing links

Examples:
    link_skill.py ~/.agents/skills/my-skill
    link_skill.py ./.agents/skills/my-skill --project-root /path/to/repo
    link_skill.py /path/to/my-skill --targets claude
    link_skill.py ~/.agents/skills/my-skill --status
"""

import sys
import os
from pathlib import Path

# ─── Default link targets ───────────────────────────────────────────
# Claude Code official docs define ~/.claude/skills and .claude/skills.
# Antigravity official docs define ~/.gemini/antigravity/skills globally and
# .agents/skills at the workspace level.
# OpenAI official Codex docs confirm Skills support, but do not currently
# publish a repository on-disk skill directory convention. This implementation
# uses ~/.codex/skills and .codex/skills as the local compatibility path for
# the Codex app/CLI environment on this machine.
LINK_TARGETS = {
    "claude": ".claude/skills",
    "codex":  ".codex/skills",
    "antigravity": ".gemini/antigravity/skills",
}

USER_DEFAULT_TARGETS = ["claude", "codex", "antigravity"]
PROJECT_DEFAULT_TARGETS = ["claude", "codex"]


def resolve_skill_path(raw_path):
    """Resolve and validate the skill source path."""
    skill_path = Path(raw_path).expanduser().resolve()
    if not skill_path.is_dir():
        print(f"❌ Error: Not a directory: {skill_path}")
        return None
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: No SKILL.md found in {skill_path}")
        return None
    return skill_path


def get_target_dir(tool_name):
    """Return the absolute path of a tool's skills directory."""
    rel = LINK_TARGETS.get(tool_name)
    if rel is None:
        return None
    return Path.home() / rel


def get_project_target_dir(tool_name, project_root):
    """Return the absolute path of a tool's project-local skills directory."""
    rel = LINK_TARGETS.get(tool_name)
    if rel is None:
        return None
    project_root = Path(project_root).expanduser().resolve()
    if tool_name == "antigravity":
        return project_root / ".agents" / "skills"
    return project_root / rel


def default_targets(project_root=None):
    """Return the default target list for user or project scope."""
    return PROJECT_DEFAULT_TARGETS if project_root is not None else USER_DEFAULT_TARGETS


def is_project_native_antigravity_skill(skill_path, project_root):
    """Return True when the skill already lives in Antigravity's native project path."""
    if project_root is None:
        return False
    native_dir = get_project_target_dir("antigravity", project_root)
    return skill_path.parent == native_dir


def compute_relative_symlink(link_location, target_real_path):
    """
    Compute a relative symlink value from link_location to target_real_path.
    Both arguments must be absolute resolved paths.
    """
    return os.path.relpath(target_real_path, link_location.parent)


def link_skill(skill_path, targets=None, force=False, project_root=None):
    """
    Create symlinks for a skill in the specified tool directories.

    Args:
        skill_path: Resolved Path to the skill directory
        targets: List of tool names, or None for all
        force: If True, overwrite existing non-matching symlinks

    Returns:
        (created, skipped, warnings) counts
    """
    if targets is None:
        targets = default_targets(project_root)

    skill_name = skill_path.name
    created, skipped, warnings = 0, 0, 0

    for tool in targets:
        if tool == "antigravity" and project_root is not None:
            native_dir = get_project_target_dir(tool, project_root)
            if is_project_native_antigravity_skill(skill_path, project_root):
                print(f"  ✓  {tool}: native project skill path {native_dir} (no link needed)")
                skipped += 1
            else:
                print(f"  ⚠  {tool}: project skills must live under {native_dir}; no link created")
                warnings += 1
            continue

        target_dir = (
            get_project_target_dir(tool, project_root)
            if project_root is not None
            else get_target_dir(tool)
        )
        if target_dir is None:
            print(f"  ⚠  Unknown tool: {tool}")
            warnings += 1
            continue

        # Ensure target skills directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        link_path = target_dir / skill_name
        rel_target = compute_relative_symlink(link_path, skill_path)

        if link_path.is_symlink():
            existing = os.readlink(link_path)
            # Normalize: resolve relative to the link's parent
            existing_resolved = (link_path.parent / existing).resolve()
            if existing_resolved == skill_path:
                print(f"  ✓  {tool}: already linked (skipped)")
                skipped += 1
                continue
            else:
                if force:
                    link_path.unlink()
                    print(f"  ⚡ {tool}: overwriting (was → {existing})")
                else:
                    print(f"  ⚠  {tool}: exists but points to {existing} (use --force to overwrite)")
                    warnings += 1
                    continue
        elif link_path.exists():
            print(f"  ⚠  {tool}: {link_path} exists as a real directory/file, skipping")
            warnings += 1
            continue

        # Create the symlink
        link_path.symlink_to(rel_target)
        print(f"  ✅ {tool}: {link_path} → {rel_target}")
        created += 1

    return created, skipped, warnings


def unlink_skill(skill_path, targets=None, project_root=None):
    """
    Remove symlinks for a skill from tool directories.

    Returns:
        (removed, not_found) counts
    """
    if targets is None:
        targets = default_targets(project_root)

    skill_name = skill_path.name
    removed, not_found = 0, 0

    for tool in targets:
        if tool == "antigravity" and project_root is not None:
            print(f"  -  {tool}: project scope uses native .agents/skills path")
            not_found += 1
            continue

        target_dir = (
            get_project_target_dir(tool, project_root)
            if project_root is not None
            else get_target_dir(tool)
        )
        if target_dir is None:
            continue

        link_path = target_dir / skill_name

        if link_path.is_symlink():
            link_path.unlink()
            print(f"  🗑  {tool}: removed {link_path}")
            removed += 1
        else:
            print(f"  -  {tool}: no link found")
            not_found += 1

    return removed, not_found


def status_skill(skill_path, targets=None, project_root=None):
    """
    Display the symlink status of a skill across the selected tools.
    """
    if targets is None:
        targets = default_targets(project_root)

    skill_name = skill_path.name
    scope_label = (
        f"project {Path(project_root).expanduser().resolve()}"
        if project_root is not None
        else "user"
    )
    print(f"\n📋 Link status for: {skill_name}")
    print(f"   Source: {skill_path}")
    print(f"   Scope: {scope_label}\n")

    for tool in targets:
        if tool == "antigravity" and project_root is not None:
            native_dir = get_project_target_dir(tool, project_root)
            if is_project_native_antigravity_skill(skill_path, project_root):
                print(f"  ✅ {tool:12s} native project path ({native_dir})")
            else:
                print(f"  ⚠  {tool:12s} expected source under {native_dir}")
            continue

        target_dir = (
            get_project_target_dir(tool, project_root)
            if project_root is not None
            else get_target_dir(tool)
        )
        if target_dir is None:
            continue

        link_path = target_dir / skill_name

        if link_path.is_symlink():
            dest = os.readlink(link_path)
            dest_resolved = (link_path.parent / dest).resolve()
            if dest_resolved == skill_path:
                print(f"  ✅ {tool:8s} → {dest} (correct)")
            else:
                print(f"  ⚠  {tool:8s} → {dest} (MISMATCH, expected → {skill_path})")
        elif link_path.exists():
            print(f"  📁 {tool:8s}   real directory (not a symlink)")
        else:
            print(f"  ❌ {tool:8s}   not linked")


def parse_targets(targets_str):
    """Parse comma-separated target list."""
    targets = [t.strip().lower() for t in targets_str.split(",") if t.strip()]
    valid = []
    for t in targets:
        if t in LINK_TARGETS:
            valid.append(t)
        else:
            print(f"⚠  Unknown target '{t}'. Available: {', '.join(LINK_TARGETS.keys())}")
    return valid if valid else None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage symlinks for multi-tool skill discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/.agents/skills/my-skill              # Link to user-level targets
  %(prog)s ./.agents/skills/my-skill --project-root .  # Link to project-local tool dirs
  %(prog)s ./my-skill --targets claude,codex,antigravity
  %(prog)s ~/.agents/skills/my-skill --status     # Show link status
  %(prog)s ~/.agents/skills/my-skill --unlink     # Remove all links
        """,
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--targets",
        help="Comma-separated tool names (default: claude,codex,antigravity for user scope; claude,codex for project scope)",
    )
    parser.add_argument(
        "--project-root",
        help="Project root for project-scoped links (uses <project-root>/.agents/skills as the real source, plus project .claude/.codex mappings)",
    )
    parser.add_argument("--status", action="store_true", help="Show link status only")
    parser.add_argument("--unlink", action="store_true", help="Remove links")
    parser.add_argument("--force", action="store_true", help="Overwrite existing non-matching links")

    args = parser.parse_args()

    # Resolve skill path
    skill_path = resolve_skill_path(args.skill_path)
    if skill_path is None:
        sys.exit(1)

    # Parse targets
    targets = parse_targets(args.targets) if args.targets else None
    project_root = args.project_root

    # Dispatch
    if args.status:
        status_skill(skill_path, targets, project_root=project_root)
    elif args.unlink:
        print(f"🗑  Unlinking: {skill_path.name}")
        removed, not_found = unlink_skill(skill_path, targets, project_root=project_root)
        print(f"\nDone: {removed} removed, {not_found} not found")
    else:
        print(f"🔗 Linking: {skill_path.name}")
        created, skipped, warnings = link_skill(
            skill_path,
            targets,
            force=args.force,
            project_root=project_root,
        )
        print(f"\nDone: {created} created, {skipped} skipped, {warnings} warnings")

    sys.exit(0)


if __name__ == "__main__":
    main()
