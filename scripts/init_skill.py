#!/usr/bin/env python3
"""Create a minimal canonical Skill source.

The initializer chooses ownership layout and invocation mode. It creates
SKILL.md plus only the host policy required to preserve that invocation intent;
branch-specific resources are added when the Skill actually needs them.
"""

import argparse
import re
import sys
from pathlib import Path


MAX_SKILL_NAME_LENGTH = 64
DEFAULT_GLOBAL_HUB = (Path.home() / ".agents" / "skills").resolve()
LAYOUTS = {
    "user-native": "user_native",
    "project-native": "project_native",
    "repo-product": "repo_product",
    "generated-product": "generated_product",
}

SKILL_TEMPLATE = """---
name: {skill_name}
description: "{description_todo}"
{invocation_line}---

# {skill_title}

[TODO: State the job this skill owns. Keep shared execution steps here; disclose
branch-only reference behind a pointer that names when to read it. If the skill
has ordered steps, end every step with a checkable and exhaustive completion
criterion. Create scripts, references, assets, or evals only when the work
actually needs them.]
"""


def title_case_skill_name(skill_name):
    """Convert a hyphenated Skill name to a display title."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def validate_skill_name(skill_name):
    """Validate portable Skill naming constraints."""
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        return False, "Skill name must be hyphen-case (lowercase letters, digits, hyphens only)."
    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        return False, "Skill name cannot start/end with hyphen or contain consecutive hyphens."
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        return False, (
            f"Skill name is too long ({len(skill_name)} chars). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH}."
        )
    return True, None


def init_skill(skill_name, path, invocation="model"):
    """Create one minimal Skill source and return its directory."""
    if invocation not in {"model", "user"}:
        raise ValueError("invocation must be 'model' or 'user'")

    skill_dir = Path(path).expanduser().resolve() / skill_name
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        description_todo = (
            "[TODO: Name the distinct trigger branches in user-intent terms.]"
            if invocation == "model"
            else "[TODO: Write a one-line human-facing summary.]"
        )
        invocation_line = "disable-model-invocation: true\n" if invocation == "user" else ""
        content = SKILL_TEMPLATE.format(
            skill_name=skill_name,
            skill_title=title_case_skill_name(skill_name),
            description_todo=description_todo,
            invocation_line=invocation_line,
        )
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        if invocation == "user":
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir()
            (agents_dir / "openai.yaml").write_text(
                "policy:\n  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
    except OSError as exc:
        print(f"❌ Error creating Skill: {exc}")
        return None

    print(f"✅ Created minimal Skill source: {skill_dir}")
    print("Next: replace the TODOs, add only required resources, then run quick_validate.")
    return skill_dir


def default_layout_path(layout, project_root=None):
    """Return the canonical parent directory for a declared ownership shape."""
    if layout == "user-native":
        return DEFAULT_GLOBAL_HUB
    if project_root is None:
        raise ValueError(f"--layout {layout} requires --project-root")

    root = Path(project_root).expanduser().resolve()
    if layout == "project-native":
        return root / ".agents" / "skills"
    if layout == "repo-product":
        return root / "skills"
    if layout == "generated-product":
        return root / "skills" / "src"
    raise ValueError(f"Unknown layout: {layout}")


def auto_link(skill_dir, project_root=None):
    """Project a new source only after explicit --link authorization."""
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from link_skill import link_skill, resolve_skill_path

    skill_path = resolve_skill_path(str(skill_dir))
    if skill_path is None:
        print("⚠  Could not link Skill (invalid path)")
        return
    print("\n🔗 Linking to configured default hosts...")
    created, skipped, warnings = link_skill(skill_path, project_root=project_root)
    print(f"   Done: {created} created, {skipped} skipped, {warnings} warnings")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a minimal canonical Skill source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s manual-review --invocation user --path ~/.agents/skills
  %(prog)s repo-review --layout repo-product --project-root /path/to/repo
  %(prog)s repo-review --project-root /path/to/repo --link
        """,
    )
    parser.add_argument("skill_name", help="Hyphen-case Skill name")
    parser.add_argument("--path", help="Canonical parent directory")
    parser.add_argument("--project-root", help="Project root for project-owned layouts")
    parser.add_argument(
        "--layout",
        choices=sorted(LAYOUTS),
        help="Ownership shape; defaults to user-native or project-native",
    )
    parser.add_argument(
        "--invocation",
        choices=("model", "user"),
        default="model",
        help="model enables autonomous discovery; user requires explicit invocation",
    )
    parser.add_argument(
        "--link",
        action="store_true",
        help="After creation, project the Skill to configured default hosts",
    )
    args = parser.parse_args()

    skill_name = args.skill_name.strip()
    valid, error_message = validate_skill_name(skill_name)
    if not valid:
        parser.error(error_message)

    layout = args.layout or ("project-native" if args.project_root else "user-native")
    try:
        target_path = args.path or str(default_layout_path(layout, args.project_root))
    except ValueError as exc:
        parser.error(str(exc))

    print(f"🚀 Initializing Skill: {skill_name}")
    print(f"   Location: {target_path}")
    print(f"   Layout: {LAYOUTS[layout]}")
    print(f"   Invocation: {args.invocation}")

    result = init_skill(skill_name, target_path, invocation=args.invocation)
    if result is None:
        return 1
    if args.link:
        if layout == "generated-product":
            print(
                "⚠  generated_product source is not linked directly. Register its "
                "build and project the generated output."
            )
        else:
            auto_link(result, project_root=args.project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
