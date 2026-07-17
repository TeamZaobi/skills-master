#!/usr/bin/env python3
"""Validate repository-owned skill layout, registry, projections, and paths."""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from utils import parse_markdown_frontmatter
from toml_compat import load_toml


LAYOUTS = {"user_native", "project_native", "repo_product", "generated_product"}
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+[^)]*)?\)")
SCHEMES = ("http://", "https://", "mailto:", "data:", "skill://")


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: str = ""


def resolve_from(root, value):
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def expected_source(root, layout, name):
    if layout == "user_native":
        return (Path.home() / ".agents" / "skills" / name).resolve()
    if layout == "project_native":
        return (root / ".agents" / "skills" / name).resolve()
    if layout == "repo_product":
        return (root / "skills" / name).resolve()
    if layout == "generated_product":
        return (root / "skills" / "src" / name).resolve()
    raise ValueError(f"Unknown layout: {layout}")


class RepositoryDoctor:
    def __init__(self, project_root, registry_path=None):
        self.root = Path(project_root).expanduser().resolve()
        self.registry_path = (
            Path(registry_path).expanduser().resolve()
            if registry_path
            else self.root / "skills" / "registry.toml"
        )
        self.findings = []
        self.registry = {}
        self.projections = {}
        self.dependencies = {}

    def finding(self, level, code, message, path=""):
        self.findings.append(Finding(level, code, message, str(path) if path else ""))

    def error(self, code, message, path=""):
        self.finding("error", code, message, path)

    def warning(self, code, message, path=""):
        self.finding("warning", code, message, path)

    def info(self, code, message, path=""):
        self.finding("info", code, message, path)

    def run(self):
        if not self.registry_path.exists():
            self.error("registry_missing", "Registry file does not exist", self.registry_path)
            return self.findings

        try:
            self.registry = load_toml(self.registry_path)
        except (OSError, RuntimeError, ValueError) as exc:
            self.error("registry_unreadable", str(exc), self.registry_path)
            return self.findings

        if self.registry.get("version") != 2:
            self.error("registry_version", "Registry must declare version = 2", self.registry_path)

        root_layout = self.registry.get("layout")
        if root_layout not in LAYOUTS:
            self.error("root_layout", f"Unknown root layout: {root_layout!r}", self.registry_path)

        self._load_projections()
        self._load_dependencies()

        seen_names = set()
        seen_sources = {}
        for skill in self.registry.get("skill", []):
            name = skill.get("name")
            if not name:
                self.error("skill_name_missing", "A skill entry has no name", self.registry_path)
                continue
            if name in seen_names:
                self.error("skill_name_duplicate", f"Duplicate registry skill name: {name}")
                continue
            seen_names.add(name)

            source_value = skill.get("source")
            if not source_value:
                self.error("skill_source_missing", f"Skill {name} has no source")
                continue
            source = resolve_from(self.root, source_value)
            previous = seen_sources.get(source)
            if previous:
                self.error(
                    "skill_source_duplicate",
                    f"Skills {previous} and {name} resolve to the same canonical source",
                    source,
                )
            seen_sources[source] = name
            self._check_skill(skill, source, root_layout)

        for consumer in self.registry.get("consumer_skill", []):
            name = consumer.get("name")
            if not name:
                self.error("consumer_name_missing", "A consumer skill entry has no name")
                continue
            if name in seen_names:
                self.error("consumer_name_duplicate", f"Duplicate owned/consumer skill name: {name}")
                continue
            seen_names.add(name)
            self._check_consumer_skill(consumer)

        self._check_kimi_shadow()
        return self.findings

    def _load_projections(self):
        for projection in self.registry.get("projection", []):
            projection_id = projection.get("id")
            if not projection_id:
                self.error("projection_id_missing", "A projection entry has no id")
                continue
            if projection_id in self.projections:
                self.error("projection_id_duplicate", f"Duplicate projection id: {projection_id}")
                continue
            if not projection.get("path") or not projection.get("hosts"):
                self.error(
                    "projection_contract",
                    f"Projection {projection_id} requires path and hosts",
                )
                continue
            self.projections[projection_id] = projection

    def _load_dependencies(self):
        for dependency in self.registry.get("dependency", []):
            dependency_id = dependency.get("id")
            if not dependency_id:
                self.error("dependency_id_missing", "A dependency entry has no id")
                continue
            if dependency_id in self.dependencies:
                self.error("dependency_id_duplicate", f"Duplicate dependency id: {dependency_id}")
                continue
            root_hint = dependency.get("root_hint")
            role = dependency.get("role")
            if not root_hint or not role:
                self.error(
                    "dependency_contract",
                    f"Dependency {dependency_id} requires root_hint and role",
                )
                continue
            resolved = resolve_from(self.root, root_hint)
            item = dict(dependency)
            item["resolved_root"] = resolved
            self.dependencies[dependency_id] = item
            if not resolved.exists():
                if dependency.get("required", False):
                    self.error(
                        "dependency_required_missing",
                        f"Required dependency {dependency_id} is missing",
                        resolved,
                    )
                else:
                    self.info(
                        "dependency_optional_missing",
                        f"Optional dependency {dependency_id} is unavailable; its integration branch stays disabled",
                        resolved,
                    )

    def _check_skill(self, skill, source, root_layout):
        name = skill["name"]
        layout = skill.get("layout", root_layout)
        if layout not in LAYOUTS:
            self.error("skill_layout", f"Skill {name} has unknown layout {layout!r}", source)
            return

        expected = expected_source(self.root, layout, name)
        if source != expected:
            self.error(
                "canonical_path",
                f"Skill {name} uses {source}; {layout} requires {expected}",
                source,
            )

        skill_md = source / "SKILL.md"
        if not source.is_dir() or not skill_md.exists():
            self.error("canonical_missing", f"Skill {name} canonical directory or SKILL.md is missing", source)
            return

        try:
            frontmatter, _ = parse_markdown_frontmatter(skill_md)
        except ValueError as exc:
            self.error("frontmatter_invalid", str(exc), skill_md)
        else:
            if frontmatter.get("name") != name or source.name != name:
                self.error(
                    "name_mismatch",
                    f"Registry, directory, and frontmatter names must all equal {name}",
                    skill_md,
                )

        projection_source = source
        if layout == "generated_product":
            projection_source = self._check_generated_contract(skill, source) or source
        elif "skills/src" in source.as_posix():
            self.error(
                "phantom_source_layer",
                f"{layout} skill {name} cannot use a skills/src canonical path",
                source,
            )

        self._check_projections(skill, projection_source, layout)
        self._check_markdown_links(source)

    def _check_consumer_skill(self, consumer):
        name = consumer["name"]
        dependency_id = consumer.get("dependency")
        source_value = consumer.get("source")
        if not dependency_id or not source_value:
            self.error(
                "consumer_contract",
                f"Consumer skill {name} requires dependency and source",
            )
            return

        dependency = self.dependencies.get(dependency_id)
        if dependency is None:
            self.error(
                "consumer_dependency_unknown",
                f"Consumer skill {name} names unknown dependency {dependency_id}",
            )
            return

        relative = Path(source_value)
        if relative.is_absolute() or ".." in relative.parts:
            self.error(
                "consumer_source_unsafe",
                f"Consumer skill {name} source must stay relative to dependency {dependency_id}",
                source_value,
            )
            return

        for candidate in (self.root / "skills" / name, self.root / "skills" / "src" / name):
            if candidate.exists() and not candidate.is_symlink():
                self.error(
                    "consumer_shadow_copy",
                    f"Consumer skill {name} has a local editable shadow copy",
                    candidate,
                )

        dependency_root = dependency["resolved_root"]
        source = dependency_root / relative
        if not dependency_root.exists():
            self._check_absent_consumer_projections(consumer)
            if not dependency.get("required", False):
                self.info(
                    "consumer_optional_unavailable",
                    f"Consumer skill {name} stays disabled while dependency {dependency_id} is absent",
                    dependency_root,
                )
            return

        skill_md = source / "SKILL.md"
        if not source.is_dir() or not skill_md.exists():
            self.error(
                "consumer_source_missing",
                f"Consumer skill {name} source is missing under dependency {dependency_id}",
                source,
            )
            return
        try:
            frontmatter, _ = parse_markdown_frontmatter(skill_md)
        except ValueError as exc:
            self.error("consumer_frontmatter_invalid", str(exc), skill_md)
        else:
            if frontmatter.get("name") != name or source.name != name:
                self.error(
                    "consumer_name_mismatch",
                    f"Consumer registry, directory, and frontmatter names must all equal {name}",
                    skill_md,
                )

        self._check_projections(consumer, source, "external_consumer")

    def _check_absent_consumer_projections(self, consumer):
        for projection_id in consumer.get("targets", []):
            projection = self.projections.get(projection_id)
            if projection is None:
                self.error(
                    "projection_unknown",
                    f"Consumer skill {consumer['name']} targets unknown projection {projection_id}",
                )
                continue
            link_path = resolve_from(self.root, projection["path"]) / consumer["name"]
            if link_path.is_symlink() or link_path.exists():
                self.error(
                    "consumer_projection_stale",
                    f"Consumer skill {consumer['name']} has a projection while its dependency is absent",
                    link_path,
                )

    def _check_generated_contract(self, skill, source):
        name = skill["name"]
        required = ("build_command", "output_dir", "reproducibility_check")
        missing = [field for field in required if not skill.get(field)]
        if missing:
            self.error(
                "generated_contract",
                f"Generated skill {name} is missing: {', '.join(missing)}",
                source,
            )
            return None
        output = resolve_from(self.root, skill["output_dir"])
        dist_root = (self.root / "skills" / "dist").resolve()
        if output != dist_root and dist_root not in output.parents:
            self.error(
                "generated_output",
                f"Generated skill {name} output must stay under {dist_root}",
                output,
            )
            return None
        if not (output / "SKILL.md").exists():
            self.error(
                "generated_output_missing",
                f"Generated skill {name} output must contain SKILL.md",
                output,
            )
        return output

    def _check_projections(self, skill, source, layout):
        target_ids = skill.get("targets")
        if target_ids is None:
            target_ids = [
                projection_id
                for projection_id, projection in self.projections.items()
                if projection.get("required", True)
            ]

        for projection_id in target_ids:
            projection = self.projections.get(projection_id)
            if projection is None:
                self.error(
                    "projection_unknown",
                    f"Skill {skill['name']} targets unknown projection {projection_id}",
                )
                continue
            target_dir = resolve_from(self.root, projection["path"])
            link_path = target_dir / skill["name"]

            if layout == "project_native" and source == link_path.resolve():
                continue
            if not link_path.is_symlink():
                kind = "real path" if link_path.exists() else "missing path"
                self.error(
                    "projection_missing",
                    f"Projection {projection_id} for {skill['name']} is a {kind}, not a symlink",
                    link_path,
                )
                continue

            raw = Path(os.readlink(link_path))
            direct_target = raw if raw.is_absolute() else link_path.parent / raw
            if direct_target.is_symlink():
                self.error(
                    "projection_chain",
                    f"Projection {projection_id} points to another projection",
                    link_path,
                )
            if not direct_target.exists():
                self.error(
                    "projection_dangling",
                    f"Projection {projection_id} is dangling",
                    link_path,
                )
                continue
            if direct_target.resolve() != source.resolve():
                self.error(
                    "projection_mismatch",
                    f"Projection {projection_id} resolves to {direct_target.resolve()}, expected {source.resolve()}",
                    link_path,
                )

    def _check_kimi_shadow(self):
        # Kimi Code discovers project skills from both .agents/skills and
        # .kimi-code/skills, and resolves a duplicated name from
        # .kimi-code/skills first. Co-projecting one canonical source to both
        # directories is redundant but harmless; two different realpaths
        # behind one name makes Kimi see different content than the other
        # hosts, so that divergence is an error.
        shared = self.root / ".agents" / "skills"
        kimi = self.root / ".kimi-code" / "skills"
        if not shared.is_dir() or not kimi.is_dir():
            return
        shared_names = {entry.name for entry in shared.iterdir()}
        for entry in sorted(kimi.iterdir()):
            if entry.name not in shared_names:
                continue
            shared_real = (shared / entry.name).resolve()
            if entry.resolve() != shared_real:
                self.error(
                    "projection_kimi_shadow",
                    f"Kimi Code resolves {entry.name} from .kimi-code/skills first, "
                    f"but it points to {entry.resolve()} while .agents/skills points to {shared_real}",
                    entry,
                )

    def _check_markdown_links(self, source):
        for markdown in source.rglob("*.md"):
            try:
                content = markdown.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                self.warning("markdown_encoding", "Could not decode Markdown as UTF-8", markdown)
                continue
            for match in MARKDOWN_LINK.finditer(content):
                raw = match.group(1).strip("<>")
                if not raw or raw.startswith("#") or raw.startswith(SCHEMES):
                    continue
                target_text = raw.split("#", 1)[0]
                if not target_text or any(token in target_text for token in ("<", ">", "{", "}")):
                    continue
                target = (markdown.parent / target_text).resolve()
                if self.root == target or self.root in target.parents:
                    if not target.exists():
                        self.error("internal_link_missing", f"Markdown target does not exist: {raw}", markdown)
                    elif source != target and source not in target.parents:
                        self.warning(
                            "package_external_local",
                            f"Markdown link leaves the packaged skill: {raw}",
                            markdown,
                        )
                    continue

                dependency = self._dependency_for_path(target)
                if dependency is None:
                    self.error(
                        "external_dependency_undeclared",
                        f"External Markdown target is not declared in registry v2: {raw}",
                        markdown,
                    )
                elif target.exists():
                    self.info(
                        "external_dependency_resolved",
                        f"External target resolves through dependency {dependency}",
                        markdown,
                    )

    def _dependency_for_path(self, target):
        for dependency_id, dependency in self.dependencies.items():
            root = dependency["resolved_root"]
            if target == root or root in target.parents:
                return dependency_id
        return None


def summarize(findings):
    counts = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding.level] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", help="Repository root")
    parser.add_argument("--registry", help="Registry v2 TOML path")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    args = parser.parse_args()

    doctor = RepositoryDoctor(args.project_root, args.registry)
    findings = doctor.run()
    counts = summarize(findings)

    if args.json:
        print(
            json.dumps(
                {
                    "project_root": str(doctor.root),
                    "registry": str(doctor.registry_path),
                    "counts": counts,
                    "findings": [asdict(item) for item in findings],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        for item in findings:
            suffix = f" [{item.path}]" if item.path else ""
            print(f"{item.level.upper():7s} {item.code}: {item.message}{suffix}")
        print(
            f"Doctor: {counts['error']} error(s), {counts['warning']} warning(s), "
            f"{counts['info']} info finding(s)"
        )

    sys.exit(1 if counts["error"] else 0)


if __name__ == "__main__":
    main()
