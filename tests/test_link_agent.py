import tempfile
import unittest
from pathlib import Path

from scripts.link_agent import get_target_dir, render_codex_agent


class LinkAgentTests(unittest.TestCase):
    def test_current_host_target_paths(self):
        self.assertEqual(get_target_dir("claude"), Path.home() / ".claude" / "agents")
        self.assertEqual(get_target_dir("codex"), Path.home() / ".codex" / "agents")
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir).resolve()
            self.assertEqual(get_target_dir("claude", root), root / ".claude" / "agents")
            self.assertEqual(get_target_dir("codex", root), root / ".codex" / "agents")

    def test_codex_render_has_required_fields(self):
        rendered = render_codex_agent("code-reviewer", "Reviews code.", "Review carefully.")
        self.assertIn('name = "code-reviewer"', rendered)
        self.assertIn('description = "Reviews code."', rendered)
        self.assertIn('developer_instructions = "Review carefully."', rendered)


if __name__ == "__main__":
    unittest.main()
