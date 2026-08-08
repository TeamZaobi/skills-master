import tempfile
import unittest
from pathlib import Path

from scripts.check_multi_skill_boundaries import check_skills, load_skill


class MultiSkillBoundaryTests(unittest.TestCase):
    def write_skill(self, root: Path, name: str, body: str, metadata: str = "") -> Path:
        skill = root / name
        skill.mkdir()
        metadata_field = f"metadata: |\n  {metadata}\n" if metadata else ""
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Use when managing {name}.\n{metadata_field}---\n\n{body}\n",
            encoding="utf-8",
        )
        return skill

    def test_coordination_words_do_not_infer_orchestrator_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_skill(Path(tmp), "domain-owner", "Coordinate with an adjacent skill.")
            self.assertEqual(load_skill(path).role, "domain")

    def test_explicit_orchestrator_requires_ownership_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_skill(
                Path(tmp),
                "router",
                "Coordinate with adjacent skills and handoff the result.",
                "role: orchestrator",
            )
            issues = check_skills([load_skill(path)])
            self.assertIn("orchestrator_missing_ownership_boundary", {item.kind for item in issues})

    def test_explicit_orchestrator_accepts_activation_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_skill(
                Path(tmp),
                "router",
                "Activation boundary: route only lifecycle delivery. Coordinate with adjacent skills.",
                "role: orchestrator",
            )
            issues = check_skills([load_skill(path)])
            self.assertNotIn("orchestrator_missing_ownership_boundary", {item.kind for item in issues})


if __name__ == "__main__":
    unittest.main()
