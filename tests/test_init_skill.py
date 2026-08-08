import tempfile
import unittest
from pathlib import Path

from scripts.init_skill import init_skill, validate_skill_name


class InitSkillTests(unittest.TestCase):
    def test_user_invoked_template_is_minimal(self):
        with tempfile.TemporaryDirectory() as tempdir:
            skill = init_skill("manual-review", Path(tempdir), invocation="user")

            self.assertIsNotNone(skill)
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", text)
            self.assertEqual(
                (skill / "agents" / "openai.yaml").read_text(encoding="utf-8"),
                "policy:\n  allow_implicit_invocation: false\n",
            )
            self.assertNotIn("## Resources", text)
            self.assertFalse((skill / "scripts").exists())
            self.assertFalse((skill / "references").exists())
            self.assertFalse((skill / "assets").exists())

    def test_model_invoked_template_omits_disable_flag(self):
        with tempfile.TemporaryDirectory() as tempdir:
            skill = init_skill("route-review", Path(tempdir), invocation="model")

            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("disable-model-invocation", text)

    def test_skill_and_ai_are_legal_name_tokens(self):
        self.assertEqual(validate_skill_name("skill-audit"), (True, None))
        self.assertEqual(validate_skill_name("ai-review"), (True, None))


if __name__ == "__main__":
    unittest.main()
