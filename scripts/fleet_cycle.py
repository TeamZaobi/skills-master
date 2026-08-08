#!/usr/bin/env python3
"""Run one evidence-bound, non-model Skills fleet governance cycle."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "scripts" / "fleet_scan.py"
CONTENT_AUDIT = ROOT / "scripts" / "content_audit.py"
DOCTOR = ROOT / "scripts" / "doctor.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a read-only structural and content governance cycle")
    parser.add_argument("--output-root", required=True, help="New or existing directory for cycle receipts")
    parser.add_argument("--policy", required=True, help="Explicit deployment-specific fleet policy")
    parser.add_argument("--previous-ledger", help="Optional prior structural finding ledger")
    return parser.parse_args()


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        command,
        cwd=str(cwd or ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess, label: str) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed ({result.returncode}): {result.stderr or result.stdout}")


def git_state(repo: Path) -> dict:
    head = run(["git", "rev-parse", "HEAD"], repo)
    status = run(["git", "status", "--porcelain=v1"], repo)
    return {
        "head": head.stdout.strip() if head.returncode == 0 else "",
        "worktree_clean": status.returncode == 0 and not status.stdout.strip(),
    }


def build_registry_receipt(registries: list[dict]) -> dict:
    results = []
    for registry in registries:
        repo = Path(registry["repo"])
        doctor = run([sys.executable, str(DOCTOR), "--json", str(repo)], ROOT)
        try:
            payload = json.loads(doctor.stdout) if doctor.stdout.strip() else {}
        except json.JSONDecodeError:
            payload = {}
        counts = payload.get("counts", {})
        results.append({
            "repo": str(repo),
            **git_state(repo),
            "registry_version": registry.get("version"),
            "registry_sha256": registry.get("registry_sha256", ""),
            "exit_code": doctor.returncode,
            "errors": counts.get("error", 1 if doctor.returncode else 0),
            "warnings": counts.get("warning", 0),
        })
    clean = sum(1 for item in results if item["exit_code"] == 0 and item["errors"] == 0)
    return {
        "schema": "fleet-registry-doctor-receipt.v1",
        "doctor": str(DOCTOR),
        "doctor_sha256": sha256(DOCTOR),
        "doctor_source_state": "live_worktree",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "registries_tested": len(results),
            "clean": clean,
            "not_clean": len(results) - clean,
            "total_errors": sum(item["errors"] for item in results),
            "total_warnings": sum(item["warnings"] for item in results),
        },
        "results": results,
    }


def combined_summary(structural: dict, content: dict, output_root: Path) -> dict:
    return {
        "schema": "skills-fleet-governance-cycle.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_root": str(output_root),
        "structural": structural,
        "content": content,
        "four_clean": {
            **structural["four_clean"],
            "content_predictability_clean": {
                "status": "clean" if content.get("content_predictability_clean") else "not_clean",
                "audited": content.get("audited", 0),
                "static_attention": content.get("static_attention", 0),
                "tier_a_external_eval_pending": content.get("tier_a_external_eval_pending", 0),
            },
        },
    }


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).expanduser().resolve()
    policy = Path(args.policy).expanduser().resolve()
    discovery = output_root / "discovery-pass"
    final = output_root / "final"
    quality = output_root / "quality" / "skills-fleet-content-quality-profile.v1.json"
    receipt_path = output_root / "registry-doctor-receipt.v1.json"

    discovery_command = [
        sys.executable, str(SCANNER), "--policy", str(policy), "--output-dir", str(discovery)
    ]
    if args.previous_ledger:
        discovery_command.extend(["--previous-ledger", str(Path(args.previous_ledger).expanduser().resolve())])
    discovery_result = run(discovery_command)
    require_success(discovery_result, "discovery scan")

    inventory = json.loads((discovery / "inventory.v1.json").read_text(encoding="utf-8"))
    registry_receipt = build_registry_receipt(inventory.get("registries", []))
    output_root.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(registry_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    final_command = [
        sys.executable,
        str(SCANNER),
        "--policy", str(policy),
        "--output-dir", str(final),
        "--previous-ledger", str(discovery / "finding-ledger.v1.json"),
        "--registry-receipt", str(receipt_path),
    ]
    final_result = run(final_command)
    require_success(final_result, "final scan")

    content_result = run([
        sys.executable,
        str(CONTENT_AUDIT),
        "--inventory", str(final / "inventory.v1.json"),
        "--policy", str(policy),
        "--output", str(quality),
    ])
    require_success(content_result, "content audit")

    structural_summary = json.loads((final / "summary.v1.json").read_text(encoding="utf-8"))
    content_summary = json.loads(quality.read_text(encoding="utf-8"))["summary"]
    summary = combined_summary(structural_summary, content_summary, output_root)
    (output_root / "cycle-summary.v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary["four_clean"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
