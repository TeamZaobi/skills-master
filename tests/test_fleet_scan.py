import json
import hashlib
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

    def run_scan(self, output, previous=None, registry_receipt=None):
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
        if registry_receipt:
            command.extend(["--registry-receipt", str(registry_receipt)])
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

    def test_terminal_previous_finding_is_observed_but_not_counted_open(self):
        dangling = self.user_codex / "accepted-missing"
        dangling.symlink_to("../../.agents/skills/accepted-missing")
        first = self.root / "terminal-first"
        self.run_scan(first)
        payload = json.loads((first / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        finding = next(item for item in payload["findings"] if item["category"] == "dangling_projection")
        finding["status"] = "accepted"
        reviewed = self.root / "terminal-reviewed.json"
        reviewed.write_text(json.dumps(payload), encoding="utf-8")

        second = self.root / "terminal-second"
        summary = self.run_scan(second, reviewed)

        self.assertEqual(summary["severity_counts"]["error"], 1)
        self.assertEqual(summary["open_severity_counts"]["error"], 0)
        self.assertEqual(summary["four_clean"]["runtime_discovery_clean"]["status"], "clean")
        self.assertEqual(summary["four_clean"]["inventory_clean"]["status"], "clean")

    def test_registry_clean_receipt_is_bound_to_registry_and_doctor_digests(self):
        project = self.projects / "registry-project"
        (project / ".git").mkdir(parents=True)
        registry = project / "skills" / "registry.toml"
        registry.parent.mkdir(parents=True)
        registry.write_text("version = 2\n", encoding="utf-8")
        doctor = Path(__file__).resolve().parent.parent / "scripts" / "doctor.py"
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        receipt = self.root / "registry-receipt.json"
        receipt.write_text(json.dumps({
            "schema": "fleet-registry-doctor-receipt.v1",
            "doctor": str(doctor),
            "doctor_sha256": digest(doctor),
            "executed_at": "2026-01-01T00:00:00Z",
            "results": [{
                "repo": str(project),
                "registry_sha256": digest(registry),
                "exit_code": 0,
                "errors": 0,
            }],
        }), encoding="utf-8")

        first = self.root / "registry-proof-first"
        clean = self.run_scan(first, registry_receipt=receipt)
        self.assertEqual(clean["four_clean"]["registry_clean"]["status"], "clean")

        registry.write_text("version = 2\nowner = \"changed\"\n", encoding="utf-8")
        second = self.root / "registry-proof-stale"
        stale = self.run_scan(second, registry_receipt=receipt)
        proof = stale["four_clean"]["registry_clean"]
        self.assertEqual(proof["status"], "not_clean")
        self.assertEqual(proof["stale_registry_receipts"], [str(project.resolve())])

    def test_explicit_non_active_historical_repo_is_retained_without_surface_warnings(self):
        backup = self.projects / "example-backup"
        (backup / ".git").mkdir(parents=True)
        self.write_skill(backup / ".codex" / "skills" / "legacy", "legacy")
        with self.policy.open("a", encoding="utf-8") as policy:
            policy.write(
                f'''\n[[historical.asset]]
path = "{backup}"
classification = "recovery_working_copy"
active = false
scan_project_surfaces = false
retention = "retain_until_manual_reconciliation"
evidence_digest_sha256 = "test-digest"
evidence_file_count = 1
'''
            )

        output = self.root / "historical"
        summary = self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        inventory = json.loads((output / "inventory.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]

        self.assertIn("classified_historical_repo", categories)
        self.assertNotIn("candidate_historical_repo", categories)
        self.assertNotIn("legacy_project_codex_surface", categories)
        self.assertEqual(summary["repos_discovered"], 1)
        self.assertEqual(summary["repos_scanned"], 0)
        self.assertEqual(inventory["historical_assets"][0]["path"], str(backup.resolve()))

    def test_exact_declared_frontmatter_name_mismatch_is_info_not_warning(self):
        project = self.projects / "hermes"
        (project / ".git").mkdir(parents=True)
        source = project / "skills" / "mlops" / "inference" / "vllm"
        self.write_skill(source, "serving-llms-vllm")
        with self.policy.open("a", encoding="utf-8") as policy:
            policy.write(
                f'''\n[[allowed_frontmatter_name_mismatch]]
repo = "{project}"
path = "skills/mlops/inference/vllm"
frontmatter_name = "serving-llms-vllm"
reason = "test-declared mapping"
'''
            )

        output = self.root / "allowed-mismatch"
        summary = self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]

        self.assertIn("allowed_frontmatter_name_mismatch", categories)
        self.assertNotIn("frontmatter_name_mismatch", categories)
        self.assertEqual(summary["severity_counts"]["warning"], 0)

    def test_declared_mismatch_does_not_hide_unexpected_runtime_name(self):
        project = self.projects / "hermes"
        (project / ".git").mkdir(parents=True)
        source = project / "skills" / "mlops" / "inference" / "vllm"
        self.write_skill(source, "unexpected-vllm-name")
        with self.policy.open("a", encoding="utf-8") as policy:
            policy.write(
                f'''\n[[allowed_frontmatter_name_mismatch]]
repo = "{project}"
path = "skills/mlops/inference/vllm"
frontmatter_name = "serving-llms-vllm"
reason = "test-declared mapping"
'''
            )

        output = self.root / "unexpected-mismatch"
        self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]

        self.assertIn("frontmatter_name_mismatch", categories)
        self.assertNotIn("allowed_frontmatter_name_mismatch", categories)

    def test_project_local_fork_sidecar_is_discovered_as_repo_source(self):
        project = self.projects / "local-fork"
        (project / ".git").mkdir(parents=True)
        source = project / "vendor" / "skill-forks" / "owner-repo" / "lookup"
        self.write_skill(source, "lookup")
        registry = project / "skills" / "registry.toml"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            '''version = 2

[[sidecar]]
name = "lookup"
source_mode = "project_local_fork"
source_path = "vendor/skill-forks/owner-repo/lookup"
upstream_commit = "0123456789abcdef0123456789abcdef01234567"
''',
            encoding="utf-8",
        )

        output = self.root / "local-fork-source"
        self.run_scan(output)
        inventory = json.loads((output / "inventory.v1.json").read_text(encoding="utf-8"))
        asset = next(item for item in inventory["assets"] if item["entry_path"] == str(source.resolve()))

        self.assertEqual(asset["role"], "repo_source")
        self.assertEqual(asset["discovery_label"], "project_sidecar_source")
        self.assertEqual(asset["declared"], "owned_sidecar")

    def test_project_local_fork_source_must_not_escape_repo(self):
        project = self.projects / "escaping-fork"
        (project / ".git").mkdir(parents=True)
        outside = self.projects / "outside-skill"
        self.write_skill(outside, "outside-skill")
        registry = project / "skills" / "registry.toml"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            '''version = 2

[[sidecar]]
name = "outside-skill"
source_mode = "project_local_fork"
source_path = "../outside-skill"
upstream_commit = "0123456789abcdef0123456789abcdef01234567"
''',
            encoding="utf-8",
        )

        output = self.root / "escaping-fork-source"
        self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]

        self.assertIn("invalid_declared_sidecar_source", categories)

    def test_retired_sidecar_remains_in_inventory_and_cannot_reappear_in_discovery(self):
        project = self.projects / "retired-sidecar"
        (project / ".git").mkdir(parents=True)
        registry = project / "skills" / "registry.toml"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            '''version = 2

[[retired_sidecar]]
name = "research"
upstream = "owner/repo"
retired_at = "2026-07-17"
retired_from_commit = "0123456789abcdef0123456789abcdef01234567"
replacement_owner = "lind"
reason = "No active consumer and required dependencies are absent."
rollback_ref = "governance/rollback/research"
eval_case = "retired-research-near-miss"
computed_hash = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
normalized_hash = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
body_hash = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
''',
            encoding="utf-8",
        )

        clean_output = self.root / "retired-sidecar-clean"
        self.run_scan(clean_output)
        inventory = json.loads((clean_output / "inventory.v1.json").read_text(encoding="utf-8"))
        record = next(item for item in inventory["registries"] if item["repo"] == str(project))
        self.assertEqual(record["retired_sidecars"][0]["name"], "research")
        clean_ledger = json.loads((clean_output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        clean_categories = [item["category"] for item in clean_ledger["findings"]]
        self.assertIn("declared_retired_sidecar", clean_categories)
        self.assertNotIn("retired_sidecar_projection_present", clean_categories)

        self.write_skill(project / ".agents" / "skills" / "research", "research")
        dirty_output = self.root / "retired-sidecar-resurrected"
        self.run_scan(dirty_output)
        dirty_ledger = json.loads((dirty_output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        retired = next(item for item in dirty_ledger["findings"] if item["category"] == "retired_sidecar_projection_present")
        self.assertEqual(retired["severity"], "error")

    def test_long_frontmatter_closing_delimiter_after_line_200_is_parseable(self):
        source = self.user_agents / "long-metadata"
        source.mkdir(parents=True)
        metadata_lines = "\n".join(f"  field_{index}: value" for index in range(250))
        (source / "SKILL.md").write_text(
            "---\n"
            "name: long-metadata\n"
            "description: Use when testing long frontmatter.\n"
            "metadata:\n"
            f"{metadata_lines}\n"
            "---\n"
            "\n# Long Metadata\n",
            encoding="utf-8",
        )

        output = self.root / "long-frontmatter"
        self.run_scan(output)
        ledger = json.loads((output / "finding-ledger.v1.json").read_text(encoding="utf-8"))
        categories = [item["category"] for item in ledger["findings"]]

        self.assertNotIn("frontmatter_invalid", categories)
        self.assertNotIn("frontmatter_missing_name", categories)

    def test_block_description_is_flattened_for_inventory(self):
        source = self.user_agents / "block-description"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text(
            "---\n"
            "name: block-description\n"
            "description: |\n"
            "  Use when testing\n"
            "  a multiline description.\n"
            "metadata:\n"
            "  owner: test\n"
            "---\n",
            encoding="utf-8",
        )

        output = self.root / "block-description"
        self.run_scan(output)
        inventory = json.loads((output / "inventory.v1.json").read_text(encoding="utf-8"))
        asset = next(item for item in inventory["assets"] if item["name"] == "block-description")

        self.assertEqual(asset["frontmatter"]["description"], "Use when testing a multiline description.")


if __name__ == "__main__":
    unittest.main()
