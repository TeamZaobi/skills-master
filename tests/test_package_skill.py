import unittest
from pathlib import Path

from scripts.package_skill import should_exclude


class PackageSkillTests(unittest.TestCase):
    def test_deployment_local_policy_is_excluded(self):
        self.assertTrue(should_exclude(Path("example/config/fleet-policy.local.toml")))

    def test_generic_policy_example_is_included(self):
        self.assertFalse(should_exclude(Path("example/references/fleet-policy.example.toml")))

    def test_repository_only_roots_are_excluded(self):
        for directory in (".git", ".claude", ".codepilot", "config", "evals", "tests"):
            with self.subTest(directory=directory):
                self.assertTrue(should_exclude(Path("example") / directory / "entry.txt"))


if __name__ == "__main__":
    unittest.main()
