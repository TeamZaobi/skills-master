import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_BODY = """---
name: {name}
description: Use when testing {name}.
---

# {name}
"""


class FleetScanTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.user_agents = self.root / "home" / ".agents" / "skills"
        self.user_codex = self.root / "home" / ".codex" / "skills"
        self.system = self.user_codex / ".system"
        self.projects = self.root / "projects"
        for path in (self.user_agents, self.user_codex, self.system, self.projects):
            path.mkdir(parents=True, exist_ok=True)
        self.policy = self.root / "policy.toml"
        self.policy.write_text(
            f'''version = 1
owner = "test"

[scope]
user_roots = ["{self.user_agents}", "{self.user_codex}"]
user_labels = ["user_agents", "user_codex"]
user_roles = ["user_canonical", "user_compat"]
system_roots = ["{self.system}"]
plugin_roots = []
project_root = "{self.projects}"
project_max_depth = 1
include_skills_master_repo = false

[historical]
exclude_path_fragments = ["/.git/"]
candidate_name_markers = ["backup", "副本", ".wt-"]

[[hosts]]
name = "codex"
user_roots = ["user_agents", "user_codex"]
project_roots = ["project_agents", "project_codex"]
resolution = "parallel_or_host_defined"
''',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def write_skill(self, path, name):
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(SKILL_BODY.format(name=name), encoding="utf-8")

    def run_scan(self, output, previous=None):
        command = [
            sys.executable,
            "scripts/fleet_scan.py",
            "--policy",
            str(self.policy),
            "--output-dir",
            str(output),
        ]
        if previous:
            command.extend(["--previous-ledger", str(previous)])
        env = dict(os.environ)
        env["PYTHONPYCACHEPREFIX"] = str(self.root / "pycache")
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parent.parent,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_host_collision_and_legal_cross_project_name_are_distinct(self):
        self.write_skill(self.user_agents / "collision", "collision")
        self.write_skill(self.user_codex / "collision", "collision")

        for project_name in ("alpha", "beta"):
            project = self.projects / project_name
            (project / ".git").mkdir(parents=True)
            self.write_skill(project / "skills" / "review", "review")

        output = self.root / "out"
        self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]
        self.assertIn("parallel_host_collision", categories)
        self.assertIn("legal_cross_project_same_name", categories)
        legal = [item for item in ledger["findings"] if item["category"] == "legal_cross_project_same_name"]
        self.assertTrue(all(item["severity"] == "info" for item in legal))

    def test_fingerprint_preserves_reviewed_disposition(self):
        dangling = self.user_codex / "missing"
        dangling.symlink_to("../../.agents/skills/missing")
        first = self.root / "first"
        self.run_scan(first)
        first_ledger_path = first / "finding-ledger.v1.json"
        payload = json.loads(first_ledger_path.read_text(encoding="utf-8"))
        finding = next(item for item in payload["findings"] if item["category"] == "dangling_projection")
        original_id = finding["finding_id"]
        self.assertEqual(finding["owner"], "user")
        self.assertIn("relink", finding["recommended_action"])
        finding["owner"] = "user"
        finding["disposition"] = "relink_to_canonical"
        reviewed = self.root / "reviewed-ledger.json"
        reviewed.write_text(json.dumps(payload), encoding="utf-8")

        second = self.root / "second"
        self.run_scan(second, reviewed)
        next_payload = json.loads((second / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        next_finding = next(item for item in next_payload["findings"] if item["category"] == "dangling_projection")
        self.assertEqual(next_finding["finding_id"], original_id)
        self.assertEqual(next_finding["owner"], "user")
        self.assertEqual(next_finding["disposition"], "relink_to_canonical")


if __name__ == "__main__":
    unittest.main()
