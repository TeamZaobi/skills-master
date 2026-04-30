#!/usr/bin/env python3
"""Static checker for multi-skill overlap and coordination hygiene."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from utils import parse_markdown_frontmatter


IGNORE_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "when", "then",
    "use", "using", "used", "skill", "agent", "work", "user", "users", "their",
    "your", "you", "can", "will", "only", "should", "want", "wants", "needs",
    "need", "across", "while", "over", "than", "after", "before", "create",
    "creating", "update", "updating", "optimize", "optimizing",
}
ROLE_KEYWORDS = {
    "orchestrator": {
        "orchestrate", "orchestration", "coordinate", "coordination", "delegate",
        "delegation", "handoff", "subagent", "multi-skill", "multi skill",
        "adjacent skill", "adjacent skills",
    },
}


@dataclass
class SkillInfo:
    name: str
    path: Path
    description: str
    body: str
    metadata: dict[str, str]
    role: str
    has_not_to_use: bool
    has_coordination: bool


@dataclass
class Issue:
    severity: str
    kind: str
    message: str
    skills: list[str]
    details: dict[str, object]


def parse_metadata_block(raw: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def discover_skill_dirs(paths: Iterable[str]) -> list[Path]:
    found: dict[Path, None] = {}
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            continue
        if (path / "SKILL.md").exists():
            found[path] = None
            continue
        for skill_md in path.rglob("SKILL.md"):
            if any(part in IGNORE_PARTS for part in skill_md.parts):
                continue
            found[skill_md.parent.resolve()] = None
    return sorted(found.keys())


def detect_role(description: str, body: str, metadata: dict[str, str]) -> str:
    explicit_role = metadata.get("role")
    if explicit_role:
        return explicit_role
    haystack = f"{description}\n{body}".lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return role
    return "domain"


def normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\s+", " ", lowered)
    lowered = re.sub(r"[^\w\s\u4e00-\u9fff-]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def extract_tokens(text: str) -> set[str]:
    normalized = normalize_text(text)
    tokens = {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]+", normalized)
        if len(token) > 2 and token not in STOPWORDS
    }
    for chunk in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(chunk) == 1:
            tokens.add(chunk)
            continue
        for idx in range(len(chunk) - 1):
            tokens.add(chunk[idx : idx + 2])
    return tokens


def similarity_metrics(left: str, right: str) -> dict[str, float]:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    left_tokens = extract_tokens(left)
    right_tokens = extract_tokens(right)
    intersection = left_tokens & right_tokens
    union = left_tokens | right_tokens
    jaccard = len(intersection) / len(union) if union else 0.0
    containment = len(intersection) / min(len(left_tokens), len(right_tokens)) if left_tokens and right_tokens else 0.0
    sequence = SequenceMatcher(None, left_norm, right_norm).ratio()
    return {
        "jaccard": jaccard,
        "containment": containment,
        "sequence": sequence,
    }


def load_skill(path: Path) -> SkillInfo:
    skill_md = path / "SKILL.md"
    metadata_raw, body = parse_markdown_frontmatter(skill_md)
    description = metadata_raw.get("description", "")
    metadata = parse_metadata_block(metadata_raw.get("metadata", ""))
    role = detect_role(description, body, metadata)
    lower_body = body.lower()
    has_not_to_use = any(
        phrase in lower_body
        for phrase in ("when not to use", "do not use", "not for", "should not trigger")
    )
    has_coordination = any(
        phrase in lower_body
        for phrase in ("multi-skill coordination", "adjacent skill", "adjacent skills", "handoff", "route narrow")
    )
    return SkillInfo(
        name=metadata_raw.get("name", path.name),
        path=path,
        description=description,
        body=body,
        metadata=metadata,
        role=role,
        has_not_to_use=has_not_to_use,
        has_coordination=has_coordination,
    )


def load_boundary_evals(path: Path) -> tuple[list[dict[str, object]], list[Issue]]:
    issues: list[Issue] = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        issues.append(Issue("error", "invalid_boundary_eval_json", f"{path}: {exc}", [], {}))
        return [], issues

    if not isinstance(data, list):
        issues.append(Issue("error", "invalid_boundary_eval_shape", "Boundary eval file must be a JSON array.", [], {}))
        return [], issues

    seen_queries: set[str] = set()
    validated: list[dict[str, object]] = []
    for idx, item in enumerate(data):
        location = f"{path}:{idx}"
        if not isinstance(item, dict):
            issues.append(Issue("error", "invalid_boundary_eval_item", f"{location} is not an object.", [], {}))
            continue
        query = item.get("query")
        primary = item.get("expected_primary_skill")
        route = item.get("expected_route")
        allowed = item.get("allowed_secondary_skills", [])
        forbidden = item.get("forbidden_skills", [])
        rationale = item.get("rationale")

        if not isinstance(query, str) or not query.strip():
            issues.append(Issue("error", "missing_query", f"{location} is missing a non-empty query.", [], {}))
            continue
        if query in seen_queries:
            issues.append(Issue("warning", "duplicate_query", f"Boundary eval query is duplicated: {query}", [], {}))
        seen_queries.add(query)
        if not isinstance(primary, str) or not primary.strip():
            issues.append(Issue("error", "missing_primary_skill", f"{location} is missing expected_primary_skill.", [], {}))
            continue
        if not isinstance(route, str) or not route.strip():
            issues.append(Issue("error", "missing_expected_route", f"{location} is missing expected_route.", [], {}))
            continue
        if not isinstance(allowed, list) or any(not isinstance(name, str) for name in allowed):
            issues.append(Issue("error", "invalid_allowed_secondary", f"{location} has an invalid allowed_secondary_skills list.", [], {}))
            continue
        if not isinstance(forbidden, list) or any(not isinstance(name, str) for name in forbidden):
            issues.append(Issue("error", "invalid_forbidden_skills", f"{location} has an invalid forbidden_skills list.", [], {}))
            continue
        if primary in forbidden:
            issues.append(Issue("error", "primary_is_forbidden", f"{location} lists the primary skill as forbidden.", [primary], {}))
        if primary in allowed:
            issues.append(Issue("warning", "primary_also_allowed", f"{location} lists the primary skill as a secondary skill.", [primary], {}))
        if set(allowed) & set(forbidden):
            overlap = sorted(set(allowed) & set(forbidden))
            issues.append(Issue("error", "secondary_forbidden_overlap", f"{location} lists the same skill as allowed and forbidden.", overlap, {}))
        if rationale is not None and not isinstance(rationale, str):
            issues.append(Issue("error", "invalid_rationale", f"{location} has a non-string rationale.", [], {}))

        validated.append(item)

    return validated, issues


def pair_covered(left: str, right: str, boundary_evals: list[dict[str, object]]) -> bool:
    for item in boundary_evals:
        primary = item.get("expected_primary_skill")
        allowed = set(item.get("allowed_secondary_skills", []))
        forbidden = set(item.get("forbidden_skills", []))
        mentioned = {primary} | allowed | forbidden
        if left in mentioned and right in mentioned:
            return True
    return False


def check_skills(skills: list[SkillInfo], boundary_evals: list[dict[str, object]] | None = None) -> list[Issue]:
    issues: list[Issue] = []
    by_name: dict[str, list[SkillInfo]] = {}
    for skill in skills:
        by_name.setdefault(skill.name, []).append(skill)

    for name, members in by_name.items():
        if len(members) > 1:
            issues.append(Issue(
                "error",
                "duplicate_skill_name",
                f"Multiple skills use the same name '{name}'.",
                [member.name for member in members],
                {"paths": [str(member.path) for member in members]},
            ))

    for skill in skills:
        if skill.role == "orchestrator" and not skill.has_not_to_use:
            issues.append(Issue(
                "warning",
                "orchestrator_missing_not_to_use",
                f"Orchestration-style skill '{skill.name}' does not clearly say when not to use it.",
                [skill.name],
                {"path": str(skill.path)},
            ))
        if skill.role == "orchestrator" and not skill.has_coordination:
            issues.append(Issue(
                "warning",
                "orchestrator_missing_coordination",
                f"Orchestration-style skill '{skill.name}' lacks explicit multi-skill coordination or handoff guidance.",
                [skill.name],
                {"path": str(skill.path)},
            ))

    for idx, left in enumerate(skills):
        for right in skills[idx + 1 :]:
            metrics = similarity_metrics(left.description, right.description)
            if metrics["sequence"] >= 0.90 or metrics["containment"] >= 0.92:
                issues.append(Issue(
                    "error",
                    "near_duplicate_descriptions",
                    f"'{left.name}' and '{right.name}' have near-duplicate descriptions.",
                    [left.name, right.name],
                    metrics,
                ))
                continue
            if metrics["sequence"] >= 0.72 or metrics["jaccard"] >= 0.45 or metrics["containment"] >= 0.75:
                issues.append(Issue(
                    "warning",
                    "high_description_overlap",
                    f"'{left.name}' and '{right.name}' may overlap too much in trigger surface.",
                    [left.name, right.name],
                    metrics,
                ))
                if boundary_evals and not pair_covered(left.name, right.name, boundary_evals):
                    issues.append(Issue(
                        "warning",
                        "missing_boundary_coverage",
                        f"'{left.name}' and '{right.name}' overlap, but no boundary eval mentions both skills together.",
                        [left.name, right.name],
                        metrics,
                    ))

    if boundary_evals:
        skill_names = {skill.name for skill in skills}
        for item in boundary_evals:
            primary = item["expected_primary_skill"]
            allowed = item.get("allowed_secondary_skills", [])
            forbidden = item.get("forbidden_skills", [])
            mentioned = [primary] + list(allowed) + list(forbidden)
            for name in mentioned:
                if name not in skill_names:
                    issues.append(Issue(
                        "warning",
                        "boundary_skill_not_loaded",
                        f"Boundary eval references '{name}', which is not present in the scanned skill set.",
                        [name],
                        {"query": item.get("query", "")},
                    ))

    return issues


def format_text(skills: list[SkillInfo], issues: list[Issue]) -> str:
    lines = [f"Scanned {len(skills)} skills."]
    if not issues:
        lines.append("No boundary issues found.")
        return "\n".join(lines)

    errors = sum(1 for issue in issues if issue.severity == "error")
    warnings = sum(1 for issue in issues if issue.severity == "warning")
    lines.append(f"Errors: {errors}, warnings: {warnings}")
    for issue in issues:
        owners = ", ".join(issue.skills) if issue.skills else "-"
        lines.append(f"[{issue.severity.upper()}] {issue.kind}: {issue.message} | skills={owners}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Static multi-skill boundary checker")
    parser.add_argument("paths", nargs="+", help="Skill directories or roots containing skills")
    parser.add_argument("--boundary-evals", help="Optional path to evals/boundary-evals.json")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors")
    args = parser.parse_args()

    skill_dirs = discover_skill_dirs(args.paths)
    if not skill_dirs:
        print("No skills found.", file=sys.stderr)
        return 1

    skills = [load_skill(path) for path in skill_dirs]
    boundary_evals: list[dict[str, object]] = []
    preload_issues: list[Issue] = []
    if args.boundary_evals:
        boundary_evals, preload_issues = load_boundary_evals(Path(args.boundary_evals).expanduser().resolve())

    issues = preload_issues + check_skills(skills, boundary_evals if args.boundary_evals else None)

    if args.format == "json":
        payload = {
            "skills": [
                {
                    "name": skill.name,
                    "path": str(skill.path),
                    "role": skill.role,
                    "metadata": skill.metadata,
                    "has_not_to_use": skill.has_not_to_use,
                    "has_coordination": skill.has_coordination,
                }
                for skill in skills
            ],
            "issues": [asdict(issue) for issue in issues],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(format_text(skills, issues))

    has_errors = any(issue.severity == "error" for issue in issues)
    has_warnings = any(issue.severity == "warning" for issue in issues)
    if has_errors or (args.strict and has_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
