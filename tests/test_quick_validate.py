import tempfile
import unittest
from pathlib import Path

from scripts.quick_validate import validate_skill


class QuickValidateTests(unittest.TestCase):
    def test_nested_metadata_keys_are_not_misclassified_as_top_level(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "SKILL.md").write_text(
                """---
name: nested-metadata
description: Use when validating a Skill with structured metadata.
metadata:
  author: Example Owner
  keywords:
    - one
    - two
  dependencies:
    - skill: another-skill
      required: true
---

# Nested metadata
""",
                encoding="utf-8",
            )

            valid, message = validate_skill(root)

        self.assertTrue(valid, message)

    def test_unknown_top_level_key_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "SKILL.md").write_text(
                """---
name: unknown-key
description: Use when validating an unsupported top-level key.
unexpected: true
---

# Unknown key
""",
                encoding="utf-8",
            )

            valid, message = validate_skill(root)

        self.assertFalse(valid)
        self.assertIn("Unexpected key", message)


if __name__ == "__main__":
    unittest.main()
