import tempfile
import unittest
from pathlib import Path

from scripts.init_agent import init_agent, validate_agent_name
from scripts.quick_validate import validate_agent


class InitAgentTests(unittest.TestCase):
    def test_template_is_minimal_and_valid(self):
        with tempfile.TemporaryDirectory() as tempdir:
            agent = init_agent("code-reviewer", Path(tempdir))
            self.assertIsNotNone(agent)
            text = (agent / "AGENT.md").read_text(encoding="utf-8")
            self.assertNotIn("## Responsibilities", text)
            self.assertEqual(validate_agent(agent), (True, "Agent is valid!"))

    def test_agent_and_ai_are_legal_name_tokens(self):
        self.assertEqual(validate_agent_name("agent-review"), (True, None))
        self.assertEqual(validate_agent_name("ai-review"), (True, None))


if __name__ == "__main__":
    unittest.main()
