#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> [--path <path>] [--project-root <path>] [--link | --no-link]

Examples:
    init_skill.py my-new-skill --path ~/.agents/skills           # auto-links to Claude, Codex, and Antigravity
    init_skill.py my-new-skill --path ~/.agents/skills --no-link # skip linking
    init_skill.py my-skill --project-root /path/to/repo          # create in /path/to/repo/.agents/skills and auto-link
    init_skill.py my-skill --path ./project/skills --link        # force link to Claude and Codex
"""

import argparse
import sys
import re
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
RESERVED_NAME_TOKENS = {'anthropic', 'claude', 'skill', 'ai'}
DEFAULT_GLOBAL_HUB = (Path.home() / ".agents" / "skills").resolve()


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" → "Reading" → "Creating" → "Editing"
- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"
- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"
- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" → numbered capability list
- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by the agent for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform the agent's process and reasoning.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that the agent should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the final deliverable the agent produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.

Example real scripts from other skills:
- pdf/scripts/fill_fillable_fields.py - Fills PDF form fields
- pdf/scripts/convert_pdf_to_images.py - Converts PDF pages to images
"""

def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here
    # This could be data processing, file conversion, API calls, etc.

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

Example real reference docs from other skills:
- product-management/references/communication.md - Comprehensive guide for status updates
- product-management/references/context_building.md - Deep-dive on gathering context
- bigquery/references/ - API references and query examples

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases

## Structure Suggestions

### API Reference Example
- Overview
- Authentication
- Endpoints with examples
- Error codes
- Rate limits

### Workflow Guide Example
- Prerequisites
- Step-by-step instructions
- Common patterns
- Troubleshooting
- Best practices
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the final deliverable the agent produces.

Example asset files from other skills:
- Brand guidelines: logo.png, slides_template.pptx
- Frontend builder: hello-world/ directory with HTML/React boilerplate
- Typography: custom-font.ttf, font-family.woff2
- Data: sample_data.csv, test_dataset.json

## Common Asset Types

- Templates: .pptx, .docx, boilerplate directories
- Images: .png, .jpg, .svg, .gif
- Fonts: .ttf, .otf, .woff, .woff2
- Boilerplate code: Project directories, starter files
- Icons: .ico, .svg
- Data files: .csv, .json, .xml, .yaml

Note: This is a text placeholder. Actual assets can be any file type.
"""


def title_case_skill_name(skill_name):
    """Convert hyphenated skill name to Title Case for display."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))

def validate_skill_name(skill_name):
    """Validate skill name against naming constraints."""
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        return False, "Skill name must be hyphen-case (lowercase letters, digits, hyphens only)."
    if skill_name.startswith('-') or skill_name.endswith('-') or '--' in skill_name:
        return False, "Skill name cannot start/end with hyphen or contain consecutive hyphens."
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        return False, (
            f"Skill name is too long ({len(skill_name)} chars). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH}."
        )
    reserved_hits = sorted({token for token in skill_name.split('-') if token in RESERVED_NAME_TOKENS})
    if reserved_hits:
        return False, (
            f"Skill name contains reserved token(s): {', '.join(reserved_hits)}. "
            "Use a neutral name."
        )
    return True, None


def init_skill(skill_name, path):
    """
    Initialize a new skill directory with template SKILL.md.

    Args:
        skill_name: Name of the skill
        path: Path where the skill directory should be created

    Returns:
        Path to created skill directory, or None if error
    """
    # Determine skill directory path
    skill_dir = Path(path).resolve() / skill_name

    # Check if directory already exists
    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    # Create skill directory
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ Created skill directory: {skill_dir}")
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        return None

    # Create SKILL.md from template
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("✅ Created SKILL.md")
    except Exception as e:
        print(f"❌ Error creating SKILL.md: {e}")
        return None

    # Create resource directories with example files
    try:
        # Create scripts/ directory with example script
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ Created scripts/example.py")

        # Create references/ directory with example reference doc
        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'api_reference.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ Created references/api_reference.md")

        # Create assets/ directory with example asset placeholder
        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET)
        print("✅ Created assets/example_asset.txt")
    except Exception as e:
        print(f"❌ Error creating resource directories: {e}")
        return None

    # Print next steps
    print(f"\n✅ Skill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    print("2. Customize or delete the example files in scripts/, references/, and assets/")
    print("3. Run the validator when ready to check the skill structure")

    return skill_dir


def is_global_hub(path):
    """Check if path is the global skills hub (~/.agents/skills)."""
    resolved = Path(path).expanduser().resolve()
    return resolved == DEFAULT_GLOBAL_HUB


def default_project_hub(project_root):
    """Return the shared project skill hub path."""
    return Path(project_root).expanduser().resolve() / ".agents" / "skills"


def is_project_hub(path, project_root):
    """Check if path is the shared project skill hub (<project-root>/.agents/skills)."""
    if project_root is None:
        return False
    return Path(path).expanduser().resolve() == default_project_hub(project_root)


def auto_link(skill_dir, project_root=None):
    """Link the skill to the default confirmed tool directories."""
    # Import from the same scripts directory
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from link_skill import link_skill, resolve_skill_path

    skill_path = resolve_skill_path(str(skill_dir))
    if skill_path is None:
        print("⚠  Could not link skill (invalid path)")
        return

    print("\n🔗 Linking to development tools...")
    created, skipped, warnings = link_skill(skill_path, project_root=project_root)
    print(f"   Done: {created} created, {skipped} skipped, {warnings} warnings")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new skill from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Skill name requirements:
  - Hyphen-case identifier (e.g., 'data-analyzer')
  - Lowercase letters, digits, and hyphens only
  - Max 64 characters
  - Avoid reserved tokens: anthropic, claude, skill, ai
  - Must match directory name exactly

Examples:
  %(prog)s my-new-skill --path ~/.agents/skills           # auto-links to Claude, Codex, and Antigravity
  %(prog)s my-new-skill --path ~/.agents/skills --no-link # skip auto-linking
  %(prog)s my-skill --project-root /path/to/repo          # create in /path/to/repo/.agents/skills and auto-link
  %(prog)s my-skill --path ./project/skills --link        # force link to Claude and Codex
        """,
    )
    parser.add_argument("skill_name", help="Name of the skill (hyphen-case)")
    parser.add_argument(
        "--path",
        help="Directory where the skill folder will be created (default: ~/.agents/skills or <project-root>/.agents/skills)",
    )
    parser.add_argument(
        "--project-root",
        help="Project root for project-scoped skills; default shared hub is <project-root>/.agents/skills",
    )

    link_group = parser.add_mutually_exclusive_group()
    link_group.add_argument("--link", action="store_true", default=None,
                            help="Link to the default confirmed tool directories after creation")
    link_group.add_argument("--no-link", action="store_true", default=False,
                            help="Skip auto-linking even for global hub")

    args = parser.parse_args()
    skill_name = args.skill_name.strip()
    if not skill_name:
        print("❌ Error: Skill name cannot be empty.")
        sys.exit(1)
    valid, error_message = validate_skill_name(skill_name)
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

    print(f"🚀 Initializing skill: {skill_name}")
    print(f"   Location: {target_path}")
    if args.project_root:
        print(f"   Project root: {Path(args.project_root).expanduser().resolve()}")
    print()

    result = init_skill(skill_name, target_path)

    if result:
        # Determine whether to auto-link
        should_link = args.link
        if should_link is None and not args.no_link:
            # Auto-link when creating in the global hub
            should_link = is_global_hub(target_path) or is_project_hub(target_path, args.project_root)

        if should_link:
            auto_link(result, project_root=args.project_root)

        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
