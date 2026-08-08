#!/usr/bin/env python3
"""Scope-aware, read-only inventory for a local Skills fleet.

The scanner reads Skill assets and writes only versioned inventory, ledger, and
summary receipts below an explicit output directory. It never relinks,
migrates, packages, adopts, or deletes a Skill asset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILLS_MASTER_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILLS_MASTER_ROOT))
from scripts.toml_compat import load_toml  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a local Skills fleet without mutating it")
    parser.add_argument(
        "--policy",
        required=True,
        help="Fleet policy TOML path",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for generated receipts")
    parser.add_argument(
        "--previous-ledger",
        help="Optional previous ledger whose owner, status, and disposition are carried by fingerprint",
    )
    parser.add_argument(
        "--registry-receipt",
        help="Optional fresh fleet-registry-doctor-receipt.v1 JSON used to prove registry_clean",
    )
    parser.add_argument("--no-write", action="store_true", help="Print summary without writing receipts")
    return parser.parse_args()


ARGS = parse_args()
POLICY_PATH = Path(ARGS.policy).expanduser().resolve()
OUT = Path(ARGS.output_dir).expanduser().resolve()


def load_policy() -> dict:
    return load_toml(POLICY_PATH)


POLICY = load_policy()
EXCLUDED = tuple(POLICY["historical"]["exclude_path_fragments"])
NAME_MARKERS = tuple(POLICY["historical"]["candidate_name_markers"])
HISTORICAL_ASSETS: list[dict] = []
HISTORICAL_BY_PATH: dict[str, dict] = {}
ALLOWED_NAME_MISMATCHES: dict[tuple[str, str], dict] = {}
configured_historical_assets = POLICY.get(
    "historical.asset",
    POLICY.get("historical", {}).get("asset", []),
)
for configured_asset in configured_historical_assets:
    record = dict(configured_asset)
    resolved_path = Path(record["path"]).expanduser().resolve(strict=False)
    record["path"] = str(resolved_path)
    HISTORICAL_ASSETS.append(record)
    HISTORICAL_BY_PATH[str(resolved_path)] = record

for configured_mismatch in POLICY.get("allowed_frontmatter_name_mismatch", []):
    record = dict(configured_mismatch)
    repo_path = Path(record["repo"]).expanduser().resolve(strict=False)
    source_path = (repo_path / record["path"]).resolve(strict=False)
    record["repo"] = str(repo_path)
    record["source_path"] = str(source_path)
    ALLOWED_NAME_MISMATCHES[(str(repo_path), str(source_path))] = record


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def finding_fingerprint(item: dict) -> str:
    payload = {
        "severity": item["severity"],
        "category": item["category"],
        "title": item["title"],
        "paths": sorted(item.get("paths", [])),
        "detail": item.get("detail", ""),
        "scope": item.get("scope", ""),
    }
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def frontmatter(path: Path) -> dict:
    result = {"parseable": False, "name": None, "description": None}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return result
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return result
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return result
    result["parseable"] = True
    frontmatter_lines = lines[1:end]
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.groups()
        value = value.strip().strip('"').strip("'")
        if key in {"name", "description"}:
            if key == "description" and value in {"|", ">", "|-", ">-", "|+", ">+"}:
                chunks: list[str] = []
                index += 1
                while index < len(frontmatter_lines):
                    continuation = frontmatter_lines[index]
                    if continuation and not continuation[0].isspace():
                        break
                    stripped = continuation.strip()
                    if stripped:
                        chunks.append(stripped)
                    index += 1
                result[key] = " ".join(chunks)
                continue
            result[key] = value
        index += 1
    return result


def is_excluded(path: Path) -> bool:
    rendered = str(path)
    return any(fragment in rendered for fragment in EXCLUDED)


def candidate_historical(path: Path) -> bool:
    lowered = path.name.lower()
    return any(marker.lower() in lowered for marker in NAME_MARKERS)


def repo_roots(root: Path, max_depth: int) -> list[Path]:
    found: set[Path] = set()
    if not root.is_dir():
        return []
    for first in root.iterdir():
        if not first.is_dir():
            continue
        if (first / ".git").exists():
            found.add(first)
        if max_depth >= 2:
            try:
                children = list(first.iterdir())
            except OSError:
                continue
            for second in children:
                if second.is_dir() and (second / ".git").exists():
                    found.add(second)
    return sorted(found)


assets: list[dict] = []
asset_keys: set[tuple] = set()
findings: list[dict] = []
registries: list[dict] = []


def add_finding(severity: str, category: str, title: str, paths: list[str], detail: str = "", scope: str = "") -> None:
    findings.append({
        "severity": severity,
        "category": category,
        "title": title,
        "paths": paths,
        "detail": detail,
        "scope": scope,
    })


def add_asset(entry: Path, *, label: str, role: str, scope: str, repo: str = "", declared: str = "") -> None:
    key = (str(entry), label, role, scope, repo)
    if key in asset_keys:
        return
    asset_keys.add(key)
    raw_target = ""
    target_abs = ""
    dangling = False
    target_is_symlink = False
    entry_type = "other"
    if entry.is_symlink():
        entry_type = "symlink"
        try:
            raw_target = os.readlink(entry)
            target_abs = raw_target if os.path.isabs(raw_target) else os.path.normpath(str(entry.parent / raw_target))
            dangling = not entry.exists()
            target_is_symlink = Path(target_abs).is_symlink()
        except OSError:
            dangling = True
    elif entry.is_dir():
        entry_type = "real_dir"
    elif entry.is_file():
        entry_type = "file"
    realpath = str(entry.resolve(strict=False))
    skill_path = Path(realpath) / "SKILL.md"
    skill_exists = skill_path.is_file()
    fm = frontmatter(skill_path) if skill_exists else {"parseable": False, "name": None, "description": None}
    name = fm.get("name") or entry.name
    asset = {
        "asset_id": hashlib.sha256("|".join(map(str, key)).encode()).hexdigest()[:16],
        "name": name,
        "entry_name": entry.name,
        "entry_path": str(entry),
        "entry_type": entry_type,
        "raw_target": raw_target,
        "target_abs": target_abs,
        "target_is_symlink": target_is_symlink,
        "dangling": dangling,
        "realpath": realpath,
        "scope": scope,
        "repo": repo,
        "discovery_label": label,
        "role": role,
        "declared": declared,
        "candidate_historical": candidate_historical(Path(repo)) if repo else candidate_historical(entry),
        "skill_md": str(skill_path) if skill_exists else "",
        "skill_sha256": sha256(skill_path) if skill_exists else "",
        "frontmatter": fm,
    }
    assets.append(asset)
    finding_scope = repo or scope

    if entry_type == "symlink" and dangling:
        add_finding("error", "dangling_projection", f"Dangling projection: {entry}", [str(entry)], f"target={raw_target}", finding_scope)
    elif entry_type == "symlink" and target_is_symlink:
        add_finding("error", "projection_chain", f"Projection targets another symlink: {entry}", [str(entry), target_abs], "Projection must point directly to a canonical directory.", finding_scope)
    if entry_type == "symlink" and not dangling and not skill_exists:
        add_finding("error", "projection_target_without_skill", f"Projection target has no SKILL.md: {entry}", [str(entry), realpath], "", finding_scope)
    if entry_type == "file" and role not in {"plugin_cache", "system_managed"}:
        package_suffixes = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz"}
        category = "package_in_discovery_surface" if entry.suffix.lower() in package_suffixes else "non_skill_file_in_discovery_surface"
        add_finding("warning", category, f"File in Skill discovery surface: {entry}", [str(entry)], role, finding_scope)
    if entry_type == "real_dir" and not skill_exists and role not in {"plugin_cache", "system_managed"}:
        try:
            contains_skills = any(entry.rglob("SKILL.md"))
        except OSError:
            contains_skills = False
        category = "collection_root_in_discovery_surface" if contains_skills else "non_skill_directory_in_discovery_surface"
        add_finding("warning", category, f"Directory in Skill discovery surface has no root SKILL.md: {entry}", [str(entry)], role, finding_scope)
    if role in {"user_projection", "user_compat", "project_projection", "project_compat"} and entry_type == "real_dir" and skill_exists:
        add_finding("warning", "real_directory_in_projection_surface", f"Editable-looking directory in projection surface: {entry}", [str(entry)], role, finding_scope)
    if role == "project_compat":
        add_finding("warning", "legacy_project_codex_surface", f"Project .codex/skills compatibility entry: {entry}", [str(entry)], "Classify before retirement; do not delete by directory-wide rule.", finding_scope)
    if skill_exists and not fm.get("parseable"):
        add_finding("warning", "frontmatter_invalid", f"Unparseable frontmatter: {skill_path}", [str(skill_path)], "", finding_scope)
    elif skill_exists and not fm.get("name"):
        add_finding("warning", "frontmatter_missing_name", f"Missing frontmatter name: {skill_path}", [str(skill_path)], "", finding_scope)
    elif skill_exists and role not in {"plugin_cache", "system_managed"} and fm.get("name") != entry.name:
        allowed = ALLOWED_NAME_MISMATCHES.get((str(Path(repo).resolve(strict=False)), realpath)) if repo else None
        if allowed and allowed.get("frontmatter_name") == fm.get("name"):
            add_finding(
                "info",
                "allowed_frontmatter_name_mismatch",
                f"Declared directory/runtime-name mapping: {entry}",
                [str(entry)],
                f"frontmatter={fm.get('name')}; reason={allowed.get('reason', '')}",
                finding_scope,
            )
        else:
            add_finding("warning", "frontmatter_name_mismatch", f"Directory/name mismatch: {entry}", [str(entry)], f"frontmatter={fm.get('name')}", finding_scope)


user_roots = POLICY["scope"]["user_roots"]
user_labels = POLICY["scope"]["user_labels"]
user_roles = POLICY["scope"]["user_roles"]
if not (len(user_roots) == len(user_labels) == len(user_roles)):
    raise ValueError("scope.user_roots, user_labels, and user_roles must have equal length")

for raw_root, label, role in zip(user_roots, user_labels, user_roles):
    root = Path(raw_root).expanduser()
    if not root.is_dir():
        continue
    try:
        children = sorted(root.iterdir())
    except OSError:
        continue
    for child in children:
        if raw_root.endswith("/.codex/skills") and child.name == ".system":
            continue
        if child.name.startswith(".") or child.name in {"Icon", "Icon\r"}:
            continue
        add_asset(child, label=label, role=role, scope="user")


for raw_root in POLICY["scope"]["system_roots"]:
    root = Path(raw_root).expanduser()
    if not root.is_dir():
        continue
    for child in sorted(root.iterdir()):
        if child.is_dir() or child.is_symlink():
            add_asset(child, label="codex_system", role="system_managed", scope="system")
            if (child.resolve(strict=False) / "SKILL.md").is_file():
                add_finding("info", "host_managed_asset", f"Host-managed system Skill: {child.name}", [str(child)], "Excluded from user cleanup.", "system")


for raw_root in POLICY["scope"]["plugin_roots"]:
    root = Path(raw_root).expanduser()
    if not root.is_dir():
        continue
    for skill_md in root.rglob("SKILL.md"):
        if is_excluded(skill_md):
            continue
        add_asset(skill_md.parent, label="codex_plugin_cache", role="plugin_cache", scope="plugin")


def load_registry(repo: Path) -> dict:
    path = repo / "skills" / "registry.toml"
    if not path.is_file():
        return {}
    try:
        data = load_toml(path)
    except Exception as exc:  # noqa: BLE001
        add_finding("warning", "registry_parse_error", f"Cannot parse registry: {path}", [str(path)], str(exc), str(repo))
        return {}
    record = {
        "repo": str(repo),
        "path": str(path),
        "registry_sha256": sha256(path),
        "version": data.get("version"),
        "layout": data.get("layout"),
        "canonical_dir": data.get("canonical_dir"),
        "owned": [item.get("name") for item in data.get("skill", [])],
        "consumers": [item.get("name") for item in data.get("consumer_skill", [])],
        "skills": [
            {
                "name": item.get("name"),
                "source": item.get("source"),
                "status": item.get("status"),
                "targets": item.get("targets", []),
                "origin": item.get("origin"),
            }
            for item in data.get("skill", [])
        ],
        "sidecars": [
            {
                "name": item.get("name"),
                "source_mode": item.get("source_mode", "upstream_install"),
                "source_path": item.get("source_path", ""),
                "upstream_commit": item.get("upstream_commit", ""),
                "status": item.get("status", ""),
            }
            for item in data.get("sidecar", [])
        ],
        "retired_sidecars": [
            {
                "name": item.get("name"),
                "upstream": item.get("upstream", ""),
                "retired_at": item.get("retired_at", ""),
                "retired_from_commit": item.get("retired_from_commit", ""),
                "replacement_owner": item.get("replacement_owner", ""),
                "reason": item.get("reason", ""),
                "rollback_ref": item.get("rollback_ref", ""),
                "eval_case": item.get("eval_case", ""),
                "computed_hash": item.get("computed_hash", ""),
                "normalized_hash": item.get("normalized_hash", ""),
                "body_hash": item.get("body_hash", ""),
            }
            for item in data.get("retired_sidecar", [])
        ],
    }
    registries.append(record)
    return data


repos = repo_roots(Path(POLICY["scope"]["project_root"]).expanduser(), int(POLICY["scope"]["project_max_depth"]))
skills_master = SKILLS_MASTER_ROOT
if POLICY["scope"].get("include_skills_master_repo", True) and (skills_master / ".git").exists():
    repos.append(skills_master)
discovered_repos = sorted(set(repos))
repos = []

PROJECT_LABELS = {
    ".agents/skills": ("project_agents", "project_native_or_projection"),
    ".claude/skills": ("project_claude", "project_projection"),
    ".kimi-code/skills": ("project_kimi", "project_projection"),
    ".codex/skills": ("project_codex", "project_compat"),
}


for repo in discovered_repos:
    historical = HISTORICAL_BY_PATH.get(str(repo.resolve(strict=False)))
    if historical:
        add_finding(
            "info",
            "classified_historical_repo",
            f"Classified non-active repository: {repo}",
            [str(repo)],
            json.dumps(historical, ensure_ascii=False, sort_keys=True),
            str(repo),
        )
        if not historical.get("scan_project_surfaces", historical.get("active", False)):
            continue
    repos.append(repo)
    registry = load_registry(repo)
    declared_owned = {item.get("source", ""): item.get("name", "") for item in registry.get("skill", [])}
    declared_consumers = {item.get("name", "") for item in registry.get("consumer_skill", [])}
    retired_sidecars = registry.get("retired_sidecar", [])
    retired_names = {item.get("name", "") for item in retired_sidecars if item.get("name")}
    for retired in retired_sidecars:
        add_finding(
            "info",
            "declared_retired_sidecar",
            f"Declared retired sidecar: {retired.get('name', '')}",
            [str(repo / "skills" / "registry.toml")],
            json.dumps({
                "upstream": retired.get("upstream", ""),
                "retired_at": retired.get("retired_at", ""),
                "retired_from_commit": retired.get("retired_from_commit", ""),
                "replacement_owner": retired.get("replacement_owner", ""),
                "rollback_ref": retired.get("rollback_ref", ""),
                "eval_case": retired.get("eval_case", ""),
            }, ensure_ascii=False, sort_keys=True),
            str(repo),
        )
    for sidecar in registry.get("sidecar", []):
        if sidecar.get("source_mode") != "project_local_fork":
            continue
        relative = sidecar.get("source_path", "")
        source = (repo / relative).resolve(strict=False)
        try:
            source.relative_to(repo.resolve())
        except ValueError:
            add_finding(
                "error",
                "invalid_declared_sidecar_source",
                f"Project-local sidecar source escapes its repository: {sidecar.get('name', '')}",
                [str(repo / relative)],
                "project_local_fork source_path must remain inside the declaring repository.",
                str(repo),
            )
            continue
        if not (source / "SKILL.md").is_file():
            add_finding(
                "error",
                "missing_declared_sidecar_source",
                f"Project-local sidecar source is missing: {sidecar.get('name', '')}",
                [str(source)],
                "The registry declares project_local_fork but the canonical SKILL.md is absent.",
                str(repo),
            )
            continue
        add_asset(
            source,
            label="project_sidecar_source",
            role="repo_source",
            scope="project",
            repo=str(repo),
            declared="owned_sidecar",
        )
    for rel, (label, role) in PROJECT_LABELS.items():
        root = repo / rel
        if not root.is_dir():
            continue
        try:
            children = sorted(root.iterdir())
        except OSError:
            continue
        for child in children:
            if child.name in {".DS_Store", "Icon", "Icon\r"}:
                continue
            if child.name in retired_names:
                add_finding(
                    "error",
                    "retired_sidecar_projection_present",
                    f"Retired sidecar remains in project discovery: {child}",
                    [str(child), str(repo / "skills" / "registry.toml")],
                    "Remove the live projection or reverse the retirement through an explicit registry change.",
                    str(repo),
                )
            declared = "consumer" if child.name in declared_consumers else ""
            add_asset(child, label=label, role=role, scope="project", repo=str(repo), declared=declared)

    skills_root = repo / "skills"
    if skills_root.is_dir():
        for skill_md in skills_root.rglob("SKILL.md"):
            if is_excluded(skill_md):
                continue
            parent = skill_md.parent
            rel = str(parent.relative_to(repo))
            if "/dist/" in f"/{rel}/" or rel.startswith("skills/dist/"):
                role = "generated_output"
            elif "/src/" in f"/{rel}/" or rel.startswith("skills/src/"):
                role = "legacy_or_generated_source"
            else:
                role = "repo_source"
            declared = "owned" if rel in declared_owned else ""
            add_asset(parent, label="project_skills_source", role=role, scope="project", repo=str(repo), declared=declared)
            if role == "legacy_or_generated_source" and not declared:
                add_finding("warning", "unregistered_or_legacy_source", f"Unregistered or legacy skills/src source: {parent}", [str(parent)], "A src name alone is not a build contract.", str(repo))


def host_conflicts(scope: str, repo: str = "") -> None:
    subset = [a for a in assets if a["scope"] == scope and a["skill_md"] and not a["dangling"]]
    if repo:
        subset = [a for a in subset if a["repo"] == repo]
    for host in POLICY["hosts"]:
        labels = set(host["user_roots"] if scope == "user" else host["project_roots"])
        candidates = [a for a in subset if a["discovery_label"] in labels]
        grouped: dict[str, list[dict]] = defaultdict(list)
        for asset in candidates:
            # Host discovery competes on the exposed directory slot. Frontmatter
            # mismatch is a separate finding and must not hide a slot collision.
            grouped[asset["entry_name"]].append(asset)
        for name, occurrences in grouped.items():
            realpaths = sorted({a["realpath"] for a in occurrences})
            if len(realpaths) <= 1:
                continue
            paths = sorted({a["entry_path"] for a in occurrences})
            if host["resolution"] == "ordered_precedence":
                add_finding("warning", "ordered_host_shadow", f"{host['name']} precedence shadows divergent '{name}'", paths, "; ".join(realpaths), repo or scope)
            else:
                add_finding("error", "parallel_host_collision", f"{host['name']} sees divergent '{name}' in one scope", paths, "; ".join(realpaths), repo or scope)


host_conflicts("user")
for repo in repos:
    host_conflicts("project", str(repo))


project_sources: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
for asset in assets:
    if asset["scope"] == "project" and asset["role"] in {"repo_source", "legacy_or_generated_source", "project_native_or_projection"} and asset["skill_md"]:
        project_sources[asset["name"]][asset["repo"]].add(asset["realpath"])
for name, by_repo in sorted(project_sources.items()):
    if len(by_repo) > 1:
        add_finding(
            "info",
            "legal_cross_project_same_name",
            f"Same name across independent project scopes: {name}",
            sorted(by_repo),
            "Not an error unless the assets enter the same host discovery scope or violate a declared consumer relationship.",
            "cross_project",
        )


for repo in repos:
    if candidate_historical(repo) and str(repo.resolve(strict=False)) not in HISTORICAL_BY_PATH:
        add_finding("warning", "candidate_historical_repo", f"Repository needs historical/active classification: {repo}", [str(repo)], "Do not silently exclude or delete.", str(repo))


# One physical defect may be observed through several projections. Preserve
# occurrence-level inventory, but collapse byte-identical findings in the ledger.
deduplicated: dict[tuple, dict] = {}
for finding in findings:
    key = (
        finding["severity"],
        finding["category"],
        finding["title"],
        tuple(finding["paths"]),
        finding["detail"],
        finding["scope"],
    )
    deduplicated[key] = finding
findings = list(deduplicated.values())


def default_owner(item: dict) -> str:
    scope = item.get("scope", "")
    if scope == "user":
        return "user"
    if scope == "system":
        return "host:codex"
    if scope == "plugin":
        return "host:plugin-updater"
    if scope == "cross_project":
        return "project-owners"
    if scope.startswith("/"):
        return f"repo:{scope}"
    return "unassigned"


RECOMMENDED_ACTIONS = {
    "dangling_projection": "confirm the intended consumer, then relink directly to the canonical source or retire the slot",
    "projection_chain": "replace the chain with a direct one-hop projection to the canonical source",
    "projection_target_without_skill": "map the exposed slot to a concrete Skill/router or retire the invalid slot",
    "parallel_host_collision": "select one canonical realpath for the host scope and remove the competing discovery path",
    "ordered_host_shadow": "make host precedence intentional and ensure every duplicate resolves to the same canonical realpath",
    "candidate_historical_repo": "classify active, immutable historical, recovery backup, or removable before exclusion",
    "classified_historical_repo": "retain according to the recorded classification and require a new owner decision before reactivation, relocation, or deletion",
    "legacy_project_codex_surface": "prove primary discovery in a fresh session, then declare or retire the compatibility entry",
    "real_directory_in_projection_surface": "reconcile edits into the canonical source, then replace the directory with a direct projection",
    "frontmatter_invalid": "repair the canonical source; for plugin/system assets, report to the updater instead of editing cache",
    "frontmatter_missing_name": "add the canonical name at the editable source and rerun discovery validation",
    "frontmatter_name_mismatch": "decide whether the host slot or frontmatter name is authoritative, then align at the canonical source",
    "allowed_frontmatter_name_mismatch": "retain the declared source-path/runtime-name mapping while its exact repo, path, and expected frontmatter name remain unchanged",
    "unregistered_or_legacy_source": "classify the asset shape and register or migrate the active source",
    "collection_root_in_discovery_surface": "expose concrete child Skills or create an explicit router; do not expose a collection root as a Skill",
    "non_skill_directory_in_discovery_surface": "classify the directory and move or remove it from the discovery surface",
    "package_in_discovery_surface": "archive the package outside discovery after recording digest and provenance",
    "non_skill_file_in_discovery_surface": "move documentation or metadata outside the Skill slot after preserving provenance",
    "host_managed_asset": "keep read-only and let the host updater own changes",
    "legal_cross_project_same_name": "retain as legal scoped duplication unless a shared host or declared consumer creates a collision",
}


def default_disposition(item: dict) -> str:
    category = item["category"]
    if category == "host_managed_asset":
        return "read_only_host_managed"
    if category == "legal_cross_project_same_name":
        return "allowed_scoped_duplicate"
    if category == "classified_historical_repo":
        return "retained_non_active_historical_asset"
    if category == "allowed_frontmatter_name_mismatch":
        return "allowed_source_slug_runtime_name_mapping"
    return "unresolved"


ledger = []
previous_by_fingerprint: dict[str, dict] = {}
if ARGS.previous_ledger:
    previous_path = Path(ARGS.previous_ledger).expanduser().resolve()
    try:
        previous_payload = json.loads(previous_path.read_text(encoding="utf-8"))
        for previous in previous_payload.get("findings", []):
            fingerprint = previous.get("fingerprint") or finding_fingerprint(previous)
            previous_by_fingerprint[fingerprint] = previous
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"warning: cannot load previous ledger {previous_path}: {exc}", file=sys.stderr)

for item in sorted(findings, key=lambda x: ({"error": 0, "warning": 1, "info": 2}[x["severity"]], x["category"], x["title"])):
    fingerprint = finding_fingerprint(item)
    previous = previous_by_fingerprint.get(fingerprint, {})
    owner = previous.get("owner")
    if not owner or owner == "unassigned":
        owner = default_owner(item)
    disposition = previous.get("disposition")
    if not disposition or disposition == "none_during_research":
        disposition = default_disposition(item)
    ledger.append({
        "finding_id": f"F-{fingerprint[:8].upper()}",
        "fingerprint": fingerprint,
        **item,
        "status": previous.get("status", "observed" if item["severity"] == "info" else "open"),
        "owner": owner,
        "disposition": disposition,
        "recommended_action": RECOMMENDED_ACTIONS.get(item["category"], "review and choose a bounded disposition"),
        "rollback_requirement": "record original path, link target, digest, and owner-approved restore action before mutation",
        "requires_fresh_proof": item["severity"] != "info",
    })


TERMINAL_FINDING_STATUSES = {
    "accepted",
    "closed",
    "false_positive",
    "remediated",
    "resolved",
    "retired",
    "superseded",
}
severity_counts = Counter(item["severity"] for item in ledger)
category_counts = Counter(item["category"] for item in ledger)
open_findings = [
    item for item in ledger
    if item["severity"] in {"error", "warning"}
    and item.get("status", "open").lower() not in TERMINAL_FINDING_STATUSES
]
open_severity_counts = Counter(item["severity"] for item in open_findings)
open_category_counts = Counter(item["category"] for item in open_findings)
scope_counts = Counter(item["scope"] for item in assets)
role_counts = Counter(item["role"] for item in assets)
runtime_error_categories = {"dangling_projection", "projection_chain", "projection_target_without_skill", "parallel_host_collision"}
runtime_errors = sum(
    1 for item in open_findings
    if item["severity"] == "error" and item["category"] in runtime_error_categories
)
inventory_open = len(open_findings)


def registry_clean_proof() -> dict:
    base = {"status": "not_fleetwide_proven", "registries_found": len(registries)}
    if not ARGS.registry_receipt:
        return base
    receipt_path = Path(ARGS.registry_receipt).expanduser().resolve()
    base["receipt"] = str(receipt_path)
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        base["proof_error"] = str(exc)
        return base
    if receipt.get("schema") != "fleet-registry-doctor-receipt.v1":
        base["proof_error"] = "unexpected receipt schema"
        return base
    expected = {str(Path(item["repo"]).resolve(strict=False)) for item in registries}
    expected_registry_digests = {
        str(Path(item["repo"]).resolve(strict=False)): item.get("registry_sha256", "")
        for item in registries
    }
    results = receipt.get("results", [])
    proven = {
        str(Path(item.get("repo", "")).expanduser().resolve(strict=False)): item
        for item in results
        if item.get("repo")
    }
    missing = sorted(expected - set(proven))
    extra = sorted(set(proven) - expected)
    failed = sorted(
        repo for repo in expected & set(proven)
        if proven[repo].get("exit_code") != 0 or proven[repo].get("errors", 0) != 0
    )
    stale = sorted(
        repo for repo in expected & set(proven)
        if proven[repo].get("registry_sha256") != expected_registry_digests.get(repo)
    )
    doctor_path = Path(receipt.get("doctor", "")).expanduser().resolve(strict=False)
    doctor_digest_matches = bool(
        doctor_path.is_file()
        and receipt.get("doctor_sha256")
        and receipt.get("doctor_sha256") == sha256(doctor_path)
    )
    base.update({
        "status": "clean" if not missing and not failed and not stale and doctor_digest_matches else "not_clean",
        "registries_tested": len(expected & set(proven)),
        "missing_repos": missing,
        "extra_repos": extra,
        "failed_repos": failed,
        "stale_registry_receipts": stale,
        "doctor_digest_matches": doctor_digest_matches,
        "executed_at": receipt.get("executed_at", ""),
    })
    return base


summary = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "policy": str(POLICY_PATH),
    "read_only": True,
    "repos_discovered": len(discovered_repos),
    "repos_scanned": len(repos),
    "historical_assets_classified": len(HISTORICAL_ASSETS),
    "registries_found": len(registries),
    "assets": len(assets),
    "unique_names": len({a["name"] for a in assets if a["skill_md"]}),
    "unique_realpaths": len({a["realpath"] for a in assets if a["skill_md"]}),
    "scope_counts": dict(sorted(scope_counts.items())),
    "role_counts": dict(sorted(role_counts.items())),
    "severity_counts": {key: severity_counts.get(key, 0) for key in ("error", "warning", "info")},
    "open_severity_counts": {key: open_severity_counts.get(key, 0) for key in ("error", "warning")},
    "category_counts": dict(sorted(category_counts.items())),
    "open_category_counts": dict(sorted(open_category_counts.items())),
    "terminal_finding_statuses": sorted(TERMINAL_FINDING_STATUSES),
    "four_clean": {
        "registry_clean": registry_clean_proof(),
        "runtime_discovery_clean": {"status": "clean" if runtime_errors == 0 else "not_clean", "open_errors": runtime_errors},
        "inventory_clean": {"status": "clean" if inventory_open == 0 else "not_clean", "open_error_or_warning": inventory_open},
        "content_predictability_clean": {"status": "not_fleetwide_assessed"},
    },
}

if not ARGS.no_write:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "inventory.v1.json").write_text(json.dumps({"summary": summary, "historical_assets": HISTORICAL_ASSETS, "registries": registries, "assets": assets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "finding-ledger.v1.json").write_text(json.dumps({"summary": summary, "findings": ledger}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
