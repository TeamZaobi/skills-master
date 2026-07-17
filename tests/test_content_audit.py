import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ContentAuditTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.skill = self.root / "active"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text(
            "---\nname: active\ndescription: Use when testing active content.\n---\n\n"
            "## 1. Inspect\n\nCompletion criterion: every input is checked.\n",
            encoding="utf-8",
        )
        self.plugin = self.root / "plugin"
        self.plugin.mkdir()
        (self.plugin / "SKILL.md").write_text("---\nname: plugin\ndescription: Plugin.\n---\n", encoding="utf-8")
        self.project_native = self.root / "project-native"
        self.project_native.mkdir()
        (self.project_native / "SKILL.md").write_text(
            "---\nname: project-native\ndescription: Use when testing a project Skill.\nversion: 1.0.0\n---\n",
            encoding="utf-8",
        )
        self.locked = self.root / "locked"
        self.locked.mkdir()
        (self.locked / "SKILL.md").write_text(
            "---\nname: locked\ndescription: Use when testing an installed Skill.\nversion: 1.0.0\n---\n",
            encoding="utf-8",
        )
        self.lock = self.root / "skill-lock.json"
        self.lock.write_text(json.dumps({"skills": {"locked": {"source": "upstream/skills", "sourceType": "github"}}}), encoding="utf-8")
        self.inventory = self.root / "inventory.json"
        self.inventory.write_text(json.dumps({
            "registries": [],
            "assets": [
                {
                    "name": "active", "realpath": str(self.skill), "skill_md": str(self.skill / "SKILL.md"),
                    "skill_sha256": "active-digest", "role": "user_canonical", "frontmatter": {"description": "Use when testing active content."},
                },
                {
                    "name": "plugin", "realpath": str(self.plugin), "skill_md": str(self.plugin / "SKILL.md"),
                    "skill_sha256": "plugin-digest", "role": "plugin_cache", "frontmatter": {"description": "Plugin."},
                },
                {
                    "name": "project-native", "realpath": str(self.project_native), "skill_md": str(self.project_native / "SKILL.md"),
                    "skill_sha256": "project-digest", "role": "project_native_or_projection", "entry_type": "real_dir",
                    "repo": str(self.root / "project"), "frontmatter": {"description": "Use when testing a project Skill."},
                },
                {
                    "name": "locked", "realpath": str(self.locked), "skill_md": str(self.locked / "SKILL.md"),
                    "skill_sha256": "locked-digest", "role": "user_canonical", "entry_type": "real_dir",
                    "frontmatter": {"description": "Use when testing an installed Skill."},
                },
            ],
        }), encoding="utf-8")
        self.policy = self.root / "policy.toml"
        self.policy.write_text(f'''[[content_tier_a]]
path = "{self.skill}"
reason = "test control surface"

[content_audit]
skill_lock = "{self.lock}"
codex_native_allowed_frontmatter_keys = ["allowed-tools", "compatibility", "description", "license", "metadata", "name"]
''', encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def run_audit(self):
        output = self.root / "quality.json"
        env = dict(os.environ)
        env["PYTHONPYCACHEPREFIX"] = str(self.root / "pycache")
        subprocess.run([
            sys.executable,
            "scripts/content_audit.py",
            "--inventory", str(self.inventory),
            "--policy", str(self.policy),
            "--output", str(output),
        ], cwd=Path(__file__).resolve().parent.parent, env=env, check=True, capture_output=True, text=True)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_tier_a_requires_external_eval_and_plugin_is_tier_c(self):
        payload = self.run_audit()
        self.assertEqual(payload["summary"]["tier_a"], 1)
        self.assertEqual(payload["summary"]["tier_b"], 2)
        self.assertEqual(payload["summary"]["tier_c_inventory_only"], 1)
        active = next(item for item in payload["profiles"] if item["name"] == "active")
        self.assertEqual(active["external_eval"], "pending")
        self.assertIn("external_eval_pending", [item["category"] for item in active["findings"]])

    def test_broken_pointer_and_orphan_reference_are_reported(self):
        reference_dir = self.skill / "references"
        reference_dir.mkdir()
        (reference_dir / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\nWhen needed, read [missing](references/missing.md).\n")
        payload = self.run_audit()
        categories = [item["category"] for item in payload["profiles"][0]["findings"]]
        self.assertIn("broken_context_pointer", categories)
        self.assertIn("undisclosed_reference_file", categories)

    def test_markdown_links_inside_fenced_examples_are_not_runtime_pointers(self):
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\n```markdown\nWhen needed, read [example](MISSING.md).\n```\n")
        payload = self.run_audit()
        categories = [item["category"] for item in payload["profiles"][0]["findings"]]
        self.assertNotIn("broken_context_pointer", categories)

    def test_reference_reachable_through_index_is_not_orphaned(self):
        reference_dir = self.skill / "references"
        reference_dir.mkdir()
        (reference_dir / "index.md").write_text("Read [detail](detail.md).\n", encoding="utf-8")
        (reference_dir / "detail.md").write_text("# Detail\n", encoding="utf-8")
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\nWhen needed, read [the index](references/index.md).\n")
        payload = self.run_audit()
        profile = payload["profiles"][0]
        self.assertEqual(profile["metrics"]["orphaned_reference_files"], [])

    def test_reference_reachable_through_backtick_index_is_not_orphaned(self):
        reference_dir = self.skill / "references"
        reference_dir.mkdir()
        (reference_dir / "index.md").write_text("For detailed handling, read `detail.md`.\n", encoding="utf-8")
        (reference_dir / "detail.md").write_text("# Detail\n", encoding="utf-8")
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\nWhen needed, read `references/index.md`.\n")
        payload = self.run_audit()
        profile = payload["profiles"][0]
        self.assertEqual(profile["metrics"]["orphaned_reference_files"], [])

    def test_reference_directory_pointer_discloses_family(self):
        reference_dir = self.skill / "references"
        family_dir = reference_dir / "family"
        family_dir.mkdir(parents=True)
        (reference_dir / "index.md").write_text("For family-specific handling, inspect `family/`.\n", encoding="utf-8")
        (family_dir / "one.md").write_text("# One\n", encoding="utf-8")
        (family_dir / "two.md").write_text("# Two\n", encoding="utf-8")
        with (self.skill / "SKILL.md").open("a", encoding="utf-8") as fh:
            fh.write("\nWhen needed, read `references/index.md`.\n")
        payload = self.run_audit()
        profile = payload["profiles"][0]
        self.assertEqual(profile["metrics"]["orphaned_reference_files"], [])

    def test_project_native_real_directory_is_audited_and_extension_is_owner_finding(self):
        payload = self.run_audit()
        profile = next(item for item in payload["profiles"] if item["name"] == "project-native")
        self.assertEqual(profile["source_management"]["class"], "project_or_repo_owner")
        self.assertIn("unsupported_frontmatter_key", [item["category"] for item in profile["findings"]])

    def test_locked_install_extension_is_observed_without_local_rewrite_finding(self):
        # Locked installs are normally at ~/.agents/skills/<name>; patch inventory and lock name
        # to the actual user-root-shaped path while retaining a hermetic temporary directory.
        inventory = json.loads(self.inventory.read_text(encoding="utf-8"))
        locked_asset = next(item for item in inventory["assets"] if item["name"] == "locked")
        locked_asset["realpath"] = str(Path("~/.agents/skills/locked").expanduser())
        locked_asset["skill_md"] = str(self.locked / "SKILL.md")
        self.inventory.write_text(json.dumps(inventory), encoding="utf-8")

        # The audit groups by realpath and therefore expects SKILL.md there. Test the source
        # classifier directly instead of writing into the real user root.
        import importlib.util
        module_path = Path(__file__).resolve().parent.parent / "scripts" / "content_audit.py"
        spec = importlib.util.spec_from_file_location("content_audit", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        management = module.source_management_for(
            str(Path("~/.agents/skills/locked").expanduser().resolve()),
            locked_asset,
            [locked_asset],
            {"locked": {"source": "upstream/skills", "sourceType": "github"}},
        )
        static, findings, observations = module.dimensions_for(
            self.locked / "SKILL.md",
            "Use when testing an installed Skill.",
            module.DEFAULT_FRONTMATTER_KEYS,
            management,
        )
        self.assertEqual(management["class"], "upstream_install_lock")
        self.assertNotIn("unsupported_frontmatter_key", [item["category"] for item in findings])
        self.assertIn("source_managed_frontmatter_extension", [item["category"] for item in observations])

    def test_repo_contract_extension_is_observation_but_undeclared_extension_is_finding(self):
        import importlib.util
        module_path = Path(__file__).resolve().parent.parent / "scripts" / "content_audit.py"
        spec = importlib.util.spec_from_file_location("content_audit_contract", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        contract = {"id": "test", "extensions": ["version"], "disposition": "repo_product_contract"}
        management = {"class": "project_or_repo_owner"}
        with (self.project_native / "SKILL.md").open("a", encoding="utf-8") as fh:
            # This is outside frontmatter and should not affect the result.
            fh.write("\n# body\n")
        static, findings, observations = module.dimensions_for(
            self.project_native / "SKILL.md",
            "Use when testing a project Skill.",
            module.DEFAULT_FRONTMATTER_KEYS,
            management,
            contract,
        )
        self.assertNotIn("unsupported_frontmatter_key", [item["category"] for item in findings])
        self.assertIn("repo_managed_frontmatter_extension", [item["category"] for item in observations])


if __name__ == "__main__":
    unittest.main()
