#!/usr/bin/env python3
"""Build a tiered, read-only content-predictability profile from fleet inventory."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILLS_MASTER_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILLS_MASTER_ROOT))
from scripts.toml_compat import load_toml


TRIGGER_PATTERN = re.compile(r"\buse when\b|\bwhen\b|\bmentions?\b|用于|当用户|当任务|适用于|提到", re.I)
HEADING_PATTERN = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
EXPLICIT_STEP_HEADING = re.compile(r"^(?:step|phase|stage|步骤|阶段)\s*\d+[\s.:、-]", re.I)
NUMERIC_HEADING = re.compile(r"^\d+[\s.:、-]")
PROCEDURE_PARENT = re.compile(
    r"workflow|procedure|process|execution|implementation|工作流|流程|步骤|执行|实施",
    re.I,
)
COMPLETION_PATTERN = re.compile(
    r"completion criterion|done when|acceptance|exit criterion|\bvalidate\b|\bvalidation\b|"
    r"\bverification\b|verification checklist|完成标准|完成条件|验收|退出条件|验证|校验|自检|检查清单|终审",
    re.I,
)
NEGATION_PATTERN = re.compile(r"\bdo not\b|\bdon't\b|\bnever\b|\bmust not\b|禁止|不得|不要|切勿", re.I)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
POINTER_WORDS = re.compile(r"\bwhen\b|\bif\b|\bfor\b|\bread\b|\bsee\b|\buse\b|当|若|如果|需要|涉及|参考|参见|见", re.I)
INACTIVE_STATUS_MARKERS = ("quarantined", "reference", "planned", "inactive", "archived", "retired")
DEFAULT_FRONTMATTER_KEYS = {"allowed-tools", "compatibility", "description", "license", "metadata", "name"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit editable Skills using writing-great-skills dimensions")
    parser.add_argument("--inventory", required=True, help="inventory.v1.json produced by fleet_scan.py")
    parser.add_argument("--policy", required=True, help="fleet-policy.v1.toml with content_tier_a records")
    parser.add_argument("--output", required=True, help="Output JSON profile path")
    return parser.parse_args()


def resolve(path: str) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


def registry_statuses(inventory: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for registry in inventory.get("registries", []):
        repo = Path(registry["repo"])
        for skill in registry.get("skills", []):
            source = skill.get("source")
            if source:
                result[str((repo / source).resolve(strict=False))] = skill
    return result


def load_skill_lock(path: str | None) -> tuple[str, dict[str, dict]]:
    if not path:
        return "", {}
    lock_path = Path(path).expanduser().resolve(strict=False)
    if not lock_path.is_file():
        return str(lock_path), {}
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return str(lock_path), {}
    skills = payload.get("skills", {}) if isinstance(payload, dict) else {}
    return str(lock_path), skills if isinstance(skills, dict) else {}


def top_level_frontmatter_keys(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    keys = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:", line)
        if match:
            keys.append(match.group(1))
    return sorted(set(keys))


def source_management_for(
    realpath: str,
    representative: dict,
    occurrences: list[dict],
    skill_lock: dict[str, dict],
) -> dict:
    name = representative.get("name", "")
    user_canonical_real_dir = any(
        item.get("role") == "user_canonical" and item.get("entry_type") == "real_dir"
        for item in occurrences
    )
    locked = skill_lock.get(name) if user_canonical_real_dir else None
    expected_user_path = resolve(f"~/.agents/skills/{name}") if name else ""
    if isinstance(locked, dict) and realpath == expected_user_path:
        return {
            "class": "upstream_install_lock",
            "mutation_owner": "upstream_or_installer",
            "local_rewrite": "prohibited_without_fork",
            "source": locked.get("source", ""),
            "source_type": locked.get("sourceType", ""),
            "source_url": locked.get("sourceUrl", ""),
            "updated_at": locked.get("updatedAt", ""),
        }
    if representative.get("repo") or any(item.get("repo") for item in occurrences):
        repo = representative.get("repo") or next((item.get("repo") for item in occurrences if item.get("repo")), "")
        return {
            "class": "project_or_repo_owner",
            "mutation_owner": "project_owner",
            "local_rewrite": "owner_review_required",
            "repo": repo,
        }
    return {
        "class": "local_user_owner",
        "mutation_owner": "local_user",
        "local_rewrite": "allowed_after_evidence",
    }


def frontmatter_contract_for(realpath: str, contracts: list[dict]) -> dict | None:
    path = Path(realpath)
    for contract in contracts:
        repo = Path(contract.get("repo", "")).expanduser().resolve(strict=False)
        try:
            path.relative_to(repo)
        except ValueError:
            continue
        return {
            "id": contract.get("id", "repo-contract"),
            "repo": str(repo),
            "extensions": sorted(set(contract.get("extensions", []))),
            "legacy_extensions": sorted(set(contract.get("legacy_extensions", []))),
            "authority": str(contract.get("authority", "")),
            "disposition": contract.get("disposition", "repo_product_contract"),
            "legacy_disposition": contract.get("legacy_disposition", "repo_cleanup_candidate_no_fleet_rewrite"),
        }
    return None


def local_markdown_target(skill_root: Path, target: str) -> Path | None:
    target = target.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if any(marker in target for marker in ("{", "}", "*")):
        return None
    candidate = Path(target).expanduser()
    return candidate if candidate.is_absolute() else skill_root / candidate


def markdown_targets_outside_fences(text: str) -> list[tuple[str, str]]:
    results = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            results.extend((line, target) for target in MARKDOWN_LINK_PATTERN.findall(line))
    return results


def procedural_step_count(text: str) -> int:
    """Count headings that are actually presented as ordered procedure steps.

    Plain numbered document sections such as ``## 1. Scope`` and
    ``## 2. Examples`` are information architecture, not proof that the Skill
    exposes a multi-step workflow.  Count explicit Step/Phase headings, plus
    numeric child headings under a workflow/procedure parent.
    """
    parents: dict[int, str] = {}
    count = 0
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        parents = {parent_level: value for parent_level, value in parents.items() if parent_level < level}
        if EXPLICIT_STEP_HEADING.match(title):
            count += 1
        elif NUMERIC_HEADING.match(title) and any(PROCEDURE_PARENT.search(value) for value in parents.values()):
            count += 1
        parents[level] = title
    return count


def reachable_reference_files(skill_root: Path, skill_text: str, reference_files: list[Path]) -> set[Path]:
    known = {path.resolve(strict=False) for path in reference_files}
    reference_root = skill_root / "references"
    basename_counts = Counter(path.name for path in reference_files)

    def mentions(current_dir: Path, current_text: str) -> set[Path]:
        mentioned: set[Path] = set()
        for ref in reference_files:
            tokens = {
                ref.relative_to(skill_root).as_posix(),
                Path(os.path.relpath(ref, current_dir)).as_posix(),
            }
            if basename_counts[ref.name] == 1:
                tokens.add(ref.name)
            if any(token in current_text for token in tokens):
                mentioned.add(ref.resolve(strict=False))

        directories = {
            parent
            for ref in reference_files
            for parent in ref.parents
            if parent != reference_root and reference_root in parent.parents
        }
        for directory in directories:
            tokens = {
                directory.relative_to(skill_root).as_posix().rstrip("/") + "/",
                Path(os.path.relpath(directory, current_dir)).as_posix().rstrip("/") + "/",
            }
            if any(token in current_text for token in tokens):
                mentioned.update(
                    ref.resolve(strict=False)
                    for ref in reference_files
                    if directory in ref.parents
                )
        return mentioned

    reachable: set[Path] = set()
    queue: list[Path] = []
    for resolved in mentions(skill_root, skill_text):
        reachable.add(resolved)
        queue.append(next(ref for ref in reference_files if ref.resolve(strict=False) == resolved))
    while queue:
        current = queue.pop(0)
        try:
            current_text = current.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for resolved in mentions(current.parent, current_text):
            if resolved not in reachable:
                reachable.add(resolved)
                queue.append(next(ref for ref in reference_files if ref.resolve(strict=False) == resolved))
        for _, target in markdown_targets_outside_fences(current_text):
            clean_target = target.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
            if not clean_target or clean_target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            candidate = (current.parent / clean_target).resolve(strict=False)
            if candidate in known and candidate not in reachable:
                reachable.add(candidate)
                queue.append(candidate)
    return reachable


def dimensions_for(
    skill_md: Path,
    description: str,
    allowed_frontmatter_keys: set[str],
    source_management: dict,
    frontmatter_contract: dict | None = None,
) -> tuple[dict, list[dict], list[dict]]:
    text = skill_md.read_text(encoding="utf-8")
    skill_root = skill_md.parent
    lines = text.splitlines()
    reference_root = skill_root / "references"
    reference_files = sorted(reference_root.rglob("*.md")) if reference_root.is_dir() else []
    reachable_references = reachable_reference_files(skill_root, text, reference_files)
    orphaned = [
        str(ref.relative_to(skill_root))
        for ref in reference_files
        if ref.resolve(strict=False) not in reachable_references
    ]

    broken = []
    pointer_lines = 0
    for line, target in markdown_targets_outside_fences(text):
        if POINTER_WORDS.search(line):
            pointer_lines += 1
        candidate = local_markdown_target(skill_root, target)
        if candidate is not None and target.split("#", 1)[0].endswith(".md") and not candidate.is_file():
            broken.append(target)

    step_count = procedural_step_count(text)
    completion_count = len(COMPLETION_PATTERN.findall(text))
    negation_count = len(NEGATION_PATTERN.findall(text))
    description = description.strip()
    findings: list[dict] = []
    observations: list[dict] = []
    frontmatter_keys = top_level_frontmatter_keys(text)
    extension_keys = sorted(set(frontmatter_keys) - allowed_frontmatter_keys)
    declared_repo_extensions = sorted(
        set(extension_keys) & set((frontmatter_contract or {}).get("extensions", []))
    )
    legacy_repo_extensions = sorted(
        set(extension_keys) & set((frontmatter_contract or {}).get("legacy_extensions", []))
    )
    undeclared_extension_keys = sorted(
        set(extension_keys) - set(declared_repo_extensions) - set(legacy_repo_extensions)
    )
    if extension_keys:
        if source_management["class"] == "upstream_install_lock":
            observations.append({
                "category": "source_managed_frontmatter_extension",
                "dimension": "single_source_of_truth",
                "values": extension_keys,
                "disposition": "upstream_owned_no_local_rewrite",
            })
        else:
            if declared_repo_extensions:
                observations.append({
                    "category": "repo_managed_frontmatter_extension",
                    "dimension": "single_source_of_truth",
                    "values": declared_repo_extensions,
                    "contract": frontmatter_contract,
                    "disposition": "repo_product_contract",
                })
            if legacy_repo_extensions:
                observations.append({
                    "category": "repo_managed_legacy_frontmatter_extension",
                    "dimension": "single_source_of_truth",
                    "values": legacy_repo_extensions,
                    "contract": frontmatter_contract,
                    "disposition": (frontmatter_contract or {}).get(
                        "legacy_disposition", "repo_cleanup_candidate_no_fleet_rewrite"
                    ),
                })
        if undeclared_extension_keys and source_management["class"] != "upstream_install_lock":
            findings.append({
                "category": "unsupported_frontmatter_key",
                "dimension": "single_source_of_truth",
                "values": undeclared_extension_keys,
                "disposition": "owner_review_required",
            })

    invocation_status = "pass"
    if not description:
        invocation_status = "attention"
        findings.append({"category": "missing_description", "dimension": "invocation"})
    elif not TRIGGER_PATTERN.search(description):
        invocation_status = "manual_review"

    hierarchy_status = "pass"
    if len(lines) > 500 and not reference_files:
        hierarchy_status = "attention"
        findings.append({"category": "large_top_level_without_disclosure", "dimension": "information_hierarchy"})

    completion_status = "pass"
    if step_count >= 2 and completion_count == 0:
        completion_status = "attention"
        findings.append({"category": "ordered_steps_without_completion_markers", "dimension": "completion_criteria"})

    disclosure_status = "pass"
    if broken:
        disclosure_status = "attention"
        findings.append({"category": "broken_context_pointer", "dimension": "progressive_disclosure", "values": sorted(set(broken))})
    if orphaned:
        disclosure_status = "attention"
        findings.append({"category": "undisclosed_reference_file", "dimension": "progressive_disclosure", "values": orphaned})

    pruning_status = "pass"
    if len(lines) > 800:
        pruning_status = "attention"
        findings.append({"category": "top_level_sprawl_signal", "dimension": "pruning"})
    if negation_count >= 20:
        pruning_status = "manual_review"

    context_status = "pass"
    if len(description) > 600:
        context_status = "attention"
        findings.append({"category": "description_context_load_signal", "dimension": "context_load"})
    if len(text.encode("utf-8")) > 50_000:
        context_status = "attention"
        findings.append({"category": "top_level_context_load_signal", "dimension": "context_load"})

    dimensions = {
        "invocation": invocation_status,
        "leading_word": "manual_review",
        "information_hierarchy": hierarchy_status,
        "completion_criteria": completion_status,
        "progressive_disclosure": disclosure_status,
        "pruning": pruning_status,
        "context_load": context_status,
        "single_source_of_truth": "attention" if undeclared_extension_keys and source_management["class"] != "upstream_install_lock" else "manual_review",
    }
    metrics = {
        "lines": len(lines),
        "bytes": len(text.encode("utf-8")),
        "description_chars": len(description),
        "description_has_explicit_trigger_phrase": bool(TRIGGER_PATTERN.search(description)),
        "step_headings": step_count,
        "completion_markers": completion_count,
        "reference_files": len(reference_files),
        "context_pointer_lines": pointer_lines,
        "orphaned_reference_files": orphaned,
        "broken_markdown_targets": sorted(set(broken)),
        "negation_markers": negation_count,
        "frontmatter_top_level_keys": frontmatter_keys,
        "frontmatter_extension_keys": extension_keys,
        "frontmatter_declared_repo_extension_keys": declared_repo_extensions,
        "frontmatter_legacy_repo_extension_keys": legacy_repo_extensions,
        "frontmatter_undeclared_extension_keys": undeclared_extension_keys,
    }
    return {"dimensions": dimensions, "metrics": metrics}, findings, observations


def main() -> int:
    args = parse_args()
    inventory_path = Path(args.inventory).expanduser().resolve()
    policy_path = Path(args.policy).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    policy = load_toml(policy_path)
    tier_a = {resolve(item["path"]): item["reason"] for item in policy.get("content_tier_a", [])}
    content_policy = policy.get("content_audit", {})
    allowed_frontmatter_keys = set(content_policy.get("codex_native_allowed_frontmatter_keys", DEFAULT_FRONTMATTER_KEYS))
    lock_path, skill_lock = load_skill_lock(content_policy.get("skill_lock"))
    frontmatter_contracts = policy.get("frontmatter_contract", [])
    statuses = registry_statuses(inventory)

    grouped: dict[str, list[dict]] = defaultdict(list)
    for asset in inventory.get("assets", []):
        if asset.get("skill_md"):
            grouped[resolve(asset["realpath"])].append(asset)

    profiles = []
    tier_c_realpaths: set[str] = set()
    category_counts: Counter[str] = Counter()
    observation_counts: Counter[str] = Counter()
    source_management_counts: Counter[str] = Counter()
    for realpath, occurrences in sorted(grouped.items()):
        user_canonical = any(item["role"] == "user_canonical" for item in occurrences)
        repo_source = any(item["role"] == "repo_source" for item in occurrences)
        project_native = any(
            item.get("role") == "project_native_or_projection" and item.get("entry_type") == "real_dir"
            for item in occurrences
        )
        if not (user_canonical or repo_source or project_native):
            tier_c_realpaths.add(realpath)
            continue
        status = statuses.get(realpath, {}).get("status") or ""
        if not user_canonical and any(marker in status.lower() for marker in INACTIVE_STATUS_MARKERS):
            tier_c_realpaths.add(realpath)
            continue
        skill_md = Path(realpath) / "SKILL.md"
        if not skill_md.is_file():
            tier_c_realpaths.add(realpath)
            continue
        tier = "A" if realpath in tier_a else "B"
        representative = next(
            (item for item in occurrences if item.get("role") == "user_canonical" and item.get("entry_type") == "real_dir"),
            next(
                (item for item in occurrences if item.get("role") in {"repo_source", "project_native_or_projection"} and item.get("entry_type") == "real_dir"),
                occurrences[0],
            ),
        )
        source_management = source_management_for(realpath, representative, occurrences, skill_lock)
        frontmatter_contract = frontmatter_contract_for(realpath, frontmatter_contracts)
        if frontmatter_contract:
            source_management["frontmatter_contract"] = frontmatter_contract
        source_management_counts[source_management["class"]] += 1
        static, findings, observations = dimensions_for(
            skill_md,
            representative.get("frontmatter", {}).get("description") or "",
            allowed_frontmatter_keys,
            source_management,
            frontmatter_contract,
        )
        static_outcome = "attention" if findings else "pass"
        if tier == "A":
            findings.append({"category": "external_eval_pending", "dimension": "dynamic_evidence"})
        for finding in findings:
            category_counts[finding["category"]] += 1
        for observation in observations:
            observation_counts[observation["category"]] += 1
        profiles.append({
            "name": representative["name"],
            "tier": tier,
            "tier_reason": tier_a.get(realpath, "active editable Skill; Tier B static audit"),
            "realpath": realpath,
            "skill_md": str(skill_md),
            "skill_sha256": representative.get("skill_sha256", ""),
            "registry_status": status,
            "source_management": source_management,
            **static,
            "static_outcome": static_outcome,
            "quality_state": "external_eval_pending" if tier == "A" else static_outcome,
            "external_eval": "pending" if tier == "A" else "not_required_by_tier",
            "findings": findings,
            "observations": observations,
        })

    tier_counts = Counter(profile["tier"] for profile in profiles)
    static_counts = Counter(profile["static_outcome"] for profile in profiles)
    payload = {
        "schema": "skills-fleet-content-quality-profile.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inventory": str(inventory_path),
        "policy": str(policy_path),
        "skill_lock": lock_path,
        "rubric": "/Users/jixiaokang/.agents/skills/writing-great-skills/SKILL.md",
        "method": "Tier A and B receive the same static signals; Tier A additionally requires usage evidence and external positive/near-miss evaluation before content_predictability_clean can pass.",
        "summary": {
            "unique_skill_realpaths": len(grouped),
            "audited": len(profiles),
            "tier_a": tier_counts["A"],
            "tier_b": tier_counts["B"],
            "tier_c_inventory_only": len(tier_c_realpaths),
            "static_pass": static_counts["pass"],
            "static_attention": static_counts["attention"],
            "tier_a_external_eval_pending": sum(1 for profile in profiles if profile["tier"] == "A"),
            "finding_category_counts": dict(sorted(category_counts.items())),
            "observation_category_counts": dict(sorted(observation_counts.items())),
            "source_management_counts": dict(sorted(source_management_counts.items())),
            "content_predictability_clean": False,
        },
        "profiles": profiles,
        "tier_c_realpaths": sorted(tier_c_realpaths),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
