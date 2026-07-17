#!/usr/bin/env python3
"""
Skill Linker - Manage directory-style projections for skill discovery.

Creates/queries/removes symbolic links from a skill's editable source
directory to tool-specific skill directories. This script deliberately
models directory-style projections only.

Runtime config discovery roots are different: Hermes `skills.external_dirs`
and OpenClaw `skills.load.extraDirs` should be managed in their host config
files, then validated with `hermes skills list`, `hermes config check`,
`openclaw skills list --json`, and `openclaw config validate`. OpenClaw may
skip symlink escapes, so cover linked-out skills by adding the real parent
directory to `skills.load.extraDirs` rather than copying skill bodies.

Usage:
    link_skill.py <skill-path>                        # Link to default user-level targets
    link_skill.py <skill-path> --project-root <path> # Link into project tool dirs
    link_skill.py <skill-path> --targets claude,codex,antigravity # Link to specific targets
    link_skill.py <skill-path> --status               # Show link status
    link_skill.py <skill-path> --unlink               # Remove all links
    link_skill.py <skill-path> --unlink --targets codex  # Remove specific links
    link_skill.py --registry <registry.toml> --all       # Link every registered skill
    link_skill.py <skill-path> --force                # Overwrite existing links

Examples:
    link_skill.py ~/.agents/skills/my-skill
    link_skill.py ./.agents/skills/my-skill --project-root /path/to/repo
    link_skill.py /path/to/my-skill --targets claude
    link_skill.py ~/.agents/skills/my-skill --status
    link_skill.py --registry ./skills/registry.toml --all --status
"""

import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from toml_compat import load_toml

# ─── Default link targets ───────────────────────────────────────────
# Keep one editable source of truth and project outward to tool-local
# discovery folders. Some local setups also expose compatibility mirrors
# in addition to the primary documented path. Tools that use runtime config
# extraDirs, such as Hermes and OpenClaw, are documented in SKILL.md/README.md
# instead of being modeled here as symlink targets.
LINK_TARGETS = {
    "claude": {
        "user": [
            {"label": "claude", "path": ".claude/skills", "link_allowed": True},
        ],
        "project": [
            {"label": "claude", "path": ".claude/skills", "link_allowed": True},
        ],
    },
    "codex": {
        "user": [
            {"label": "codex", "path": ".agents/skills", "link_allowed": True},
            {"label": "codex-home", "path": ".codex/skills", "link_allowed": True},
        ],
        "project": [
            {"label": "codex", "path": ".agents/skills", "link_allowed": True},
        ],
    },
    "antigravity": {
        "user": [
            {"label": "antigravity", "path": ".gemini/antigravity/skills", "link_allowed": True},
            {"label": "gemini", "path": ".gemini/skills", "link_allowed": True},
        ],
        "project": [
            {"label": "antigravity", "path": ".agents/skills", "link_allowed": False},
        ],
    },
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


def get_target_entries(tool_name, project_root=None):
    """Return resolved target entries for the given tool and scope."""
    spec = LINK_TARGETS.get(tool_name)
    if spec is None:
        return []

    scope = "project" if project_root is not None else "user"
    base_dir = Path(project_root).expanduser().resolve() if project_root is not None else Path.home()
    entries = []
    for entry in spec[scope]:
        entries.append(
            {
                "label": entry["label"],
                "dir": (base_dir / entry["path"]).resolve(),
                "link_allowed": entry["link_allowed"],
            }
        )
    return entries


def default_targets(project_root=None):
    """Return the default target list for user or project scope."""
    return PROJECT_DEFAULT_TARGETS if project_root is not None else USER_DEFAULT_TARGETS


def is_native_skill_path(skill_path, target_dir):
    """Return True when the skill already lives in the target directory."""
    return skill_path.parent == target_dir.resolve()


def compute_relative_symlink(link_location, target_real_path):
    """
    Compute a relative symlink value from link_location to target_real_path.
    Both arguments must be absolute resolved paths.
    """
    return os.path.relpath(target_real_path, link_location.parent)


def load_registry(registry_path):
    """Load a registry v2 document and return it with its project root."""
    path = Path(registry_path).expanduser().resolve()
    registry = load_toml(path)
    if registry.get("version") != 2:
        raise ValueError(f"Registry must use version = 2: {path}")
    if path.parent.name == "skills":
        project_root = path.parent.parent
    else:
        project_root = path.parent
    return registry, project_root


def registry_dependency_sources(registry, project_root):
    """Resolve dependency ids to roots for consumer skill entries."""
    dependencies = {}
    for item in registry.get("dependency", []):
        dependency_id = item.get("id")
        root_hint = item.get("root_hint")
        if dependency_id and root_hint:
            dependencies[dependency_id] = {
                **item,
                "root": (project_root / root_hint).resolve(),
            }
    return dependencies


def registry_selected_skills(registry, project_root, selector=None, select_all=False):
    """Return owned and external-consumer sources selected from registry v2."""
    selected = []
    requested_path = Path(selector).expanduser().resolve() if selector and Path(selector).exists() else None

    for item in registry.get("skill", []):
        source = (project_root / item["source"]).resolve()
        if select_all or requested_path == source or selector == item.get("name"):
            layout = item.get("layout", registry.get("layout"))
            projection_source = (
                (project_root / item["output_dir"]).resolve()
                if layout == "generated_product" and item.get("output_dir")
                else source
            )
            selected.append(("owned", item, projection_source, True))

    dependencies = registry_dependency_sources(registry, project_root)
    for item in registry.get("consumer_skill", []):
        dependency = dependencies.get(item.get("dependency"))
        if dependency is None:
            if select_all or selector == item.get("name"):
                selected.append(("consumer", item, None, False))
            continue
        relative = Path(item.get("source", ""))
        source = dependency["root"] / relative
        if select_all or requested_path == source.resolve() or selector == item.get("name"):
            selected.append(("consumer", item, source.resolve(), dependency["root"].exists()))
    return selected


def registry_projection_entries(registry, project_root, skill_entry):
    """Resolve the projection targets declared for one registry skill."""
    projections = {item.get("id"): item for item in registry.get("projection", [])}
    requested = skill_entry.get("targets")
    if requested is None:
        requested = [
            projection_id
            for projection_id, item in projections.items()
            if item.get("required", True)
        ]

    entries = []
    for projection_id in requested:
        item = projections.get(projection_id)
        if item is None:
            raise ValueError(
                f"Skill {skill_entry.get('name')} names unknown projection {projection_id}"
            )
        entries.append(
            {
                "label": projection_id,
                "dir": (project_root / item["path"]).resolve(),
                "link_allowed": True,
            }
        )
    return entries


def link_skill_to_entries(skill_path, entries, force=False):
    """Create direct projections for an explicit list of target directories."""
    skill_name = skill_path.name
    created, skipped, warnings = 0, 0, 0

    for entry in entries:
        target_dir = entry["dir"]
        label = entry["label"]

        if is_native_skill_path(skill_path, target_dir):
            print(f"  ✓  {label}: native path {target_dir} (no link needed)")
            skipped += 1
            continue

        if not entry.get("link_allowed", True):
            print(f"  ⚠  {label}: expected source under {target_dir}; no link created")
            warnings += 1
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        link_path = target_dir / skill_name
        rel_target = compute_relative_symlink(link_path, skill_path)

        if link_path.is_symlink():
            existing = os.readlink(link_path)
            existing_resolved = (link_path.parent / existing).resolve()
            if existing_resolved == skill_path:
                print(f"  ✓  {label}: already linked (skipped)")
                skipped += 1
                continue
            if force:
                link_path.unlink()
                print(f"  ⚡ {label}: overwriting (was → {existing})")
            else:
                print(f"  ⚠  {label}: exists but points to {existing} (use --force to overwrite)")
                warnings += 1
                continue
        elif link_path.exists():
            print(f"  ⚠  {label}: {link_path} exists as a real directory/file, skipping")
            warnings += 1
            continue

        link_path.symlink_to(rel_target)
        print(f"  ✅ {label}: {link_path} → {rel_target}")
        created += 1

    return created, skipped, warnings


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

    entries = []
    for tool in targets:
        tool_entries = get_target_entries(tool, project_root)
        if not tool_entries:
            print(f"  ⚠  Unknown tool: {tool}")
            continue
        entries.extend(tool_entries)

    return link_skill_to_entries(skill_path, entries, force=force)


def unlink_skill(skill_path, targets=None, project_root=None):
    """
    Remove symlinks for a skill from tool directories.

    Returns:
        (removed, not_found) counts
    """
    if targets is None:
        targets = default_targets(project_root)

    entries = []
    for tool in targets:
        tool_entries = get_target_entries(tool, project_root)
        if not tool_entries:
            continue
        entries.extend(tool_entries)

    return unlink_skill_entries(skill_path, entries)


def unlink_skill_entries(skill_path, entries):
    """Remove projections from an explicit list of target directories."""
    skill_name = skill_path.name
    removed, not_found = 0, 0

    for entry in entries:
        target_dir = entry["dir"]
        label = entry["label"]

        if is_native_skill_path(skill_path, target_dir):
            print(f"  -  {label}: native path (no link to remove)")
            not_found += 1
            continue

        if not entry.get("link_allowed", True):
            print(f"  -  {label}: scope expects a native source")
            not_found += 1
            continue

        link_path = target_dir / skill_name

        if link_path.is_symlink():
            link_path.unlink()
            print(f"  🗑  {label}: removed {link_path}")
            removed += 1
        else:
            print(f"  -  {label}: no link found")
            not_found += 1

    return removed, not_found


def status_skill(skill_path, targets=None, project_root=None):
    """
    Display the symlink status of a skill across the selected tools.
    """
    if targets is None:
        targets = default_targets(project_root)

    scope_label = (
        f"project {Path(project_root).expanduser().resolve()}"
        if project_root is not None
        else "user"
    )
    print(f"\n📋 Link status for: {skill_path.name}")
    print(f"   Source: {skill_path}")
    print(f"   Scope: {scope_label}\n")

    entries = []
    for tool in targets:
        tool_entries = get_target_entries(tool, project_root)
        if not tool_entries:
            continue
        entries.extend(tool_entries)

    status_skill_entries(skill_path, entries)


def status_skill_entries(skill_path, entries):
    """Display projection status for explicit target directories."""
    skill_name = skill_path.name

    for entry in entries:
        target_dir = entry["dir"]
        label = entry["label"]

        if is_native_skill_path(skill_path, target_dir):
            print(f"  ✅ {label:12s} native path ({target_dir})")
            continue

        if not entry.get("link_allowed", True):
            print(f"  ⚠  {label:12s} expected source under {target_dir}")
            continue

        link_path = target_dir / skill_name

        if link_path.is_symlink():
            dest = os.readlink(link_path)
            dest_resolved = (link_path.parent / dest).resolve()
            if dest_resolved == skill_path:
                print(f"  ✅ {label:12s} → {dest} (correct)")
            else:
                print(f"  ⚠  {label:12s} → {dest} (MISMATCH, expected → {skill_path})")
        elif link_path.exists():
            print(f"  📁 {label:12s} real directory (not a symlink)")
        else:
            print(f"  ❌ {label:12s} not linked")


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
    parser.add_argument("skill_path", nargs="?", help="Path to the skill directory")
    parser.add_argument(
        "--targets",
        help="Comma-separated tool names (default: claude,codex,antigravity for user scope; claude,codex for project scope)",
    )
    parser.add_argument(
        "--project-root",
        help="Project root for project-scoped links (uses <project-root>/.agents/skills as the real source, plus project .claude and shared .agents mappings)",
    )
    parser.add_argument("--status", action="store_true", help="Show link status only")
    parser.add_argument("--unlink", action="store_true", help="Remove links")
    parser.add_argument("--force", action="store_true", help="Overwrite existing non-matching links")
    parser.add_argument("--registry", help="Registry v2 TOML file")
    parser.add_argument("--all", action="store_true", help="Operate on every skill in --registry")

    args = parser.parse_args()

    if args.registry:
        if args.targets:
            parser.error("--targets cannot be combined with --registry")
        try:
            registry, registry_root = load_registry(args.registry)
        except (OSError, RuntimeError, ValueError) as exc:
            parser.error(str(exc))

        selected = registry_selected_skills(
            registry,
            registry_root,
            selector=args.skill_path,
            select_all=args.all,
        )
        if not selected:
            parser.error("Select a registered skill by path/name, or pass --all")

        totals = [0, 0, 0]
        for kind, item, source, dependency_available in selected:
            if kind == "consumer" and not dependency_available:
                print(
                    f"\n  -  consumer {item['name']}: dependency "
                    f"{item.get('dependency')} is unavailable; projection stays disabled"
                )
                continue
            skill_path = resolve_skill_path(str(source))
            if skill_path is None:
                totals[2] += 1
                continue
            try:
                entries = registry_projection_entries(registry, registry_root, item)
            except ValueError as exc:
                print(f"  ⚠  {exc}")
                totals[2] += 1
                continue
            print(f"\n🔗 Registry {kind} skill: {item['name']}")
            if args.status:
                status_skill_entries(skill_path, entries)
            elif args.unlink:
                removed, missing = unlink_skill_entries(skill_path, entries)
                totals[0] += removed
                totals[1] += missing
            else:
                result = link_skill_to_entries(skill_path, entries, force=args.force)
                totals = [left + right for left, right in zip(totals, result)]
        sys.exit(1 if totals[2] else 0)

    if not args.skill_path:
        parser.error("skill_path is required unless --registry is used")

    skill_path = resolve_skill_path(args.skill_path)
    if skill_path is None:
        sys.exit(1)

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
