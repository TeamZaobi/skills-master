import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "fleet_cycle.py"
SPEC = importlib.util.spec_from_file_location("fleet_cycle", MODULE_PATH)
fleet_cycle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fleet_cycle)


class FleetCycleTests(unittest.TestCase):
    def test_combined_summary_keeps_content_separate_from_structural_clean(self):
        structural = {
            "four_clean": {
                "registry_clean": {"status": "clean"},
                "runtime_discovery_clean": {"status": "clean"},
                "inventory_clean": {"status": "clean"},
                "content_predictability_clean": {"status": "not_fleetwide_assessed"},
            }
        }
        content = {
            "content_predictability_clean": False,
            "audited": 10,
            "static_attention": 3,
            "tier_a_external_eval_pending": 2,
        }

        summary = fleet_cycle.combined_summary(structural, content, Path("/tmp/cycle"))

        self.assertEqual(summary["four_clean"]["registry_clean"]["status"], "clean")
        self.assertEqual(summary["four_clean"]["content_predictability_clean"]["status"], "not_clean")
        self.assertEqual(summary["four_clean"]["content_predictability_clean"]["static_attention"], 3)

    def test_registry_receipt_binds_current_registry_and_doctor_digests(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / ".git").mkdir()
            registry = repo / "skills" / "registry.toml"
            registry.parent.mkdir()
            registry.write_text("version = 2\n", encoding="utf-8")
            expected_digest = hashlib.sha256(registry.read_bytes()).hexdigest()
            completed = fleet_cycle.subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps({"counts": {"error": 0, "warning": 0}}),
                stderr="",
            )
            git_head = fleet_cycle.subprocess.CompletedProcess(args=[], returncode=0, stdout="abc\n", stderr="")
            git_clean = fleet_cycle.subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            with patch.object(fleet_cycle, "run", side_effect=[completed, git_head, git_clean]):
                receipt = fleet_cycle.build_registry_receipt([{
                    "repo": str(repo),
                    "version": 2,
                    "registry_sha256": expected_digest,
                }])

            self.assertEqual(receipt["summary"]["clean"], 1)
            self.assertEqual(receipt["results"][0]["registry_sha256"], expected_digest)
            self.assertTrue(receipt["results"][0]["worktree_clean"])


if __name__ == "__main__":
    unittest.main()
