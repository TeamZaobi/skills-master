import os
import tempfile
import unittest
from pathlib import Path

from scripts.doctor import RepositoryDoctor, expected_source, summarize


SKILL_BODY = """---
name: {name}
description: Use when testing {name}.
---

# {name}
"""

KIMI_PROJECTION = """[[projection]]
id = "kimi"
path = ".kimi-code/skills"
hosts = ["kimi"]
required = false

"""


class LayoutGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "skills").mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def write_skill(self, path, name):
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(SKILL_BODY.format(name=name), encoding="utf-8")

    def write_registry(self, body):
        path = self.root / "skills" / "registry.toml"
        path.write_text(body, encoding="utf-8")
        return path

    def direct_projection(self, directory, name, source):
        directory.mkdir(parents=True, exist_ok=True)
        link = directory / name
        link.symlink_to(os.path.relpath(source, directory))
        return link

    def run_doctor(self):
        doctor = RepositoryDoctor(self.root)
        findings = doctor.run()
        return findings, summarize(findings)

    def test_doctor_requires_registry_backed_repository(self):
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 1)
        self.assertEqual([item.code for item in findings], ["registry_missing"])

    def repo_registry(self, skill_block, dependencies="", extra_projections=""):
        return f"""version = 2
layout = "repo_product"
canonical_dir = "skills"

[[projection]]
id = "agents"
path = ".agents/skills"
hosts = ["codex", "gemini"]
required = true

[[projection]]
id = "claude"
path = ".claude/skills"
hosts = ["claude"]
required = true

{extra_projections}{skill_block}
{dependencies}
"""

    def test_repo_product_is_valid(self):
        source = self.root / "skills" / "example"
        self.write_skill(source, "example")
        self.direct_projection(self.root / ".agents" / "skills", "example", source)
        self.direct_projection(self.root / ".claude" / "skills", "example", source)
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "example"
source = "skills/example"
targets = ["agents", "claude"]
"""
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0, findings)

    def test_project_native_stays_under_agents(self):
        source = self.root / ".agents" / "skills" / "local-only"
        self.write_skill(source, "local-only")
        self.direct_projection(self.root / ".claude" / "skills", "local-only", source)
        self.write_registry(
            """version = 2
layout = "project_native"
canonical_dir = ".agents/skills"

[[projection]]
id = "agents"
path = ".agents/skills"
hosts = ["codex", "gemini"]

[[projection]]
id = "claude"
path = ".claude/skills"
hosts = ["claude"]

[[skill]]
name = "local-only"
source = ".agents/skills/local-only"
targets = ["agents", "claude"]
"""
        )
        _, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0)

    def test_user_native_contract_has_stable_path(self):
        self.assertEqual(
            expected_source(self.root, "user_native", "personal"),
            (Path.home() / ".agents" / "skills" / "personal").resolve(),
        )

    def test_generated_product_requires_and_uses_dist_output(self):
        source = self.root / "skills" / "src" / "compiled"
        output = self.root / "skills" / "dist" / "compiled"
        self.write_skill(source, "compiled")
        self.write_skill(output, "compiled")
        self.direct_projection(self.root / ".agents" / "skills", "compiled", output)
        self.direct_projection(self.root / ".claude" / "skills", "compiled", output)
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "compiled"
source = "skills/src/compiled"
layout = "generated_product"
targets = ["agents", "claude"]
build_command = "make compiled"
output_dir = "skills/dist/compiled"
reproducibility_check = "make verify-compiled"
"""
            )
        )
        _, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0)

    def test_repo_product_under_src_is_rejected(self):
        source = self.root / "skills" / "src" / "wrong"
        self.write_skill(source, "wrong")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "wrong"
source = "skills/src/wrong"
targets = []
"""
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("canonical_path", {item.code for item in findings})

    def test_generated_product_without_build_contract_is_rejected(self):
        source = self.root / "skills" / "src" / "incomplete"
        self.write_skill(source, "incomplete")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "incomplete"
source = "skills/src/incomplete"
layout = "generated_product"
targets = []
"""
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("generated_contract", {item.code for item in findings})

    def test_dangling_and_projection_chain_are_rejected(self):
        source = self.root / "skills" / "linked"
        self.write_skill(source, "linked")
        agents = self.root / ".agents" / "skills"
        claude = self.root / ".claude" / "skills"
        agents.mkdir(parents=True)
        claude.mkdir(parents=True)
        (agents / "linked").symlink_to("../../missing/linked")
        (claude / "linked").symlink_to(os.path.relpath(agents / "linked", claude))
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "linked"
source = "skills/linked"
targets = ["agents", "claude"]
"""
            )
        )
        findings, _ = self.run_doctor()
        codes = {item.code for item in findings}
        self.assertIn("projection_dangling", codes)
        self.assertIn("projection_chain", codes)

    def test_duplicate_source_is_rejected(self):
        source = self.root / "skills" / "one"
        self.write_skill(source, "one")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "one"
source = "skills/one"
targets = []

[[skill]]
name = "two"
source = "skills/one"
targets = []
"""
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("skill_source_duplicate", {item.code for item in findings})

    def test_undeclared_external_markdown_dependency_is_rejected(self):
        source = self.root / "skills" / "external-reader"
        self.write_skill(source, "external-reader")
        with (source / "SKILL.md").open("a", encoding="utf-8") as handle:
            handle.write("\n[External](../../../Sibling/README.md)\n")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "external-reader"
source = "skills/external-reader"
targets = []
"""
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("external_dependency_undeclared", {item.code for item in findings})

    def test_missing_optional_dependency_is_informational(self):
        source = self.root / "skills" / "portable"
        self.write_skill(source, "portable")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "portable"
source = "skills/portable"
targets = []
""",
                """[[dependency]]
id = "optional-sibling"
root_hint = "../OptionalSibling"
required = false
role = "integration_only"
""",
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0)
        self.assertIn("dependency_optional_missing", {item.code for item in findings})

    def test_external_consumer_projects_directly_to_dependency_source(self):
        dependency_root = self.root / "external-blackfactory"
        source = dependency_root / "skills" / "lind"
        self.write_skill(source, "lind")
        self.direct_projection(self.root / ".agents" / "skills", "lind", source)
        self.direct_projection(self.root / ".claude" / "skills", "lind", source)
        self.write_registry(
            self.repo_registry(
                "",
                """[[dependency]]
id = "blackfactory"
root_hint = "external-blackfactory"
required = false
role = "product_skill_source"

[[consumer_skill]]
name = "lind"
dependency = "blackfactory"
source = "skills/lind"
targets = ["agents", "claude"]
""",
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0, findings)

    def test_optional_external_consumer_can_stay_unprojected(self):
        self.write_registry(
            self.repo_registry(
                "",
                """[[dependency]]
id = "blackfactory"
root_hint = "missing-blackfactory"
required = false
role = "product_skill_source"

[[consumer_skill]]
name = "lind"
dependency = "blackfactory"
source = "skills/lind"
targets = ["agents", "claude"]
""",
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0, findings)
        self.assertIn("consumer_optional_unavailable", {item.code for item in findings})

    def test_external_consumer_rejects_local_editable_shadow_copy(self):
        dependency_root = self.root / "external-blackfactory"
        source = dependency_root / "skills" / "lind"
        self.write_skill(source, "lind")
        self.write_skill(self.root / "skills" / "src" / "lind", "lind")
        self.direct_projection(self.root / ".agents" / "skills", "lind", source)
        self.direct_projection(self.root / ".claude" / "skills", "lind", source)
        self.write_registry(
            self.repo_registry(
                "",
                """[[dependency]]
id = "blackfactory"
root_hint = "external-blackfactory"
required = false
role = "product_skill_source"

[[consumer_skill]]
name = "lind"
dependency = "blackfactory"
source = "skills/lind"
targets = ["agents", "claude"]
""",
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("consumer_shadow_copy", {item.code for item in findings})

    def test_kimi_projection_one_hop_is_valid(self):
        source = self.root / "skills" / "kimi-ok"
        self.write_skill(source, "kimi-ok")
        self.direct_projection(self.root / ".agents" / "skills", "kimi-ok", source)
        self.direct_projection(self.root / ".claude" / "skills", "kimi-ok", source)
        self.direct_projection(self.root / ".kimi-code" / "skills", "kimi-ok", source)
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "kimi-ok"
source = "skills/kimi-ok"
targets = ["agents", "claude", "kimi"]
""",
                extra_projections=KIMI_PROJECTION,
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0, findings)
        self.assertNotIn("projection_kimi_shadow", {item.code for item in findings})

    def test_kimi_projection_is_opt_in(self):
        source = self.root / "skills" / "shared-only"
        self.write_skill(source, "shared-only")
        self.direct_projection(self.root / ".agents" / "skills", "shared-only", source)
        self.direct_projection(self.root / ".claude" / "skills", "shared-only", source)
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "shared-only"
source = "skills/shared-only"
targets = ["agents", "claude"]
""",
                extra_projections=KIMI_PROJECTION,
            )
        )
        findings, counts = self.run_doctor()
        self.assertEqual(counts["error"], 0, findings)
        self.assertNotIn("projection_kimi_shadow", {item.code for item in findings})
        self.assertFalse((self.root / ".kimi-code" / "skills" / "shared-only").exists())

    def test_kimi_shadow_detects_diverging_duplicate(self):
        source = self.root / "skills" / "shadowed"
        self.write_skill(source, "shadowed")
        self.direct_projection(self.root / ".agents" / "skills", "shadowed", source)
        self.direct_projection(self.root / ".claude" / "skills", "shadowed", source)
        self.write_skill(self.root / ".kimi-code" / "skills" / "shadowed", "shadowed")
        self.write_registry(
            self.repo_registry(
                """[[skill]]
name = "shadowed"
source = "skills/shadowed"
targets = ["agents", "claude"]
""",
                extra_projections=KIMI_PROJECTION,
            )
        )
        findings, _ = self.run_doctor()
        self.assertIn("projection_kimi_shadow", {item.code for item in findings})


if __name__ == "__main__":
    unittest.main()
