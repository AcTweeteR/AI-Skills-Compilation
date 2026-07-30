#!/usr/bin/env python3
"""Validate the documentation-only AI catalog without making network requests."""

from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "skills" / "registry.yml"
ENTRY_DIRECTORIES = {
    "accepted": "approved",
    "candidates": "candidate",
    "watchlist": "watchlist",
    "rejected": "rejected",
}
REQUIRED_ENTRY_FIELDS = {
    "id",
    "name",
    "source",
    "status",
    "artifact_type",
    "category",
    "summary",
    "what_it_does",
    "compatibility",
    "compatibility_notes",
    "useful_for",
    "not_recommended_for",
    "risk_level",
    "risk_reasons",
    "install_allowed",
    "execution_allowed",
    "requires_sandbox",
    "approved_for_project_integration",
    "data_access",
    "review",
    "safe_usage_boundary",
    "next_action",
}
REQUIRED_WHAT_IT_DOES_FIELDS = {"plain_language", "main_features", "best_use_case"}
REQUIRED_DATA_ACCESS_FIELDS = {
    "local_files",
    "network",
    "credentials",
    "persistent_memory",
    "shell_commands",
    "git_hooks",
    "writes_files",
    "modifies_code",
}
REQUIRED_REVIEW_FIELDS = {
    "reviewed_at",
    "reviewed_by",
    "review_status",
    "evidence_checked",
    "notes",
}
ALLOWED_DATA_ACCESS_VALUES = {"yes", "no", "likely", "possible", "unknown"}
INDEX_PATHS = {
    "category": ROOT / "docs" / "catalog_by_category.md",
    "compatibility": ROOT / "docs" / "catalog_by_compatibility.md",
    "status": ROOT / "docs" / "catalog_by_status.md",
    "risk": ROOT / "docs" / "catalog_by_risk.md",
}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "assigned credential": re.compile(
        r"(?i)\b(?:api[_-]?key|token|secret|password|authorization|bearer)\b"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
    ),
    "local user path": re.compile(r"/(?:Users|home)/[^\s/]+/"),
    "private IPv4 address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "htmlcov",
    "venv",
}


def load_yaml(path: Path, errors: list[str]) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def entry_paths(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    for directory in ENTRY_DIRECTORIES:
        paths.extend(sorted((root / "skills" / directory).glob("*.yml")))
    return paths


def is_valid_public_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    hostname = parsed.hostname.casefold()
    if hostname == "localhost" or hostname.endswith((".local", ".internal")):
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return True
    return not (address.is_private or address.is_loopback or address.is_link_local)


def check_entry(
    path: Path,
    entry: Any,
    registry: dict[str, Any],
    errors: list[str],
    expected_status: str | None,
) -> None:
    label = str(path.relative_to(ROOT))
    if not isinstance(entry, dict):
        errors.append(f"{label}: top level must be a mapping")
        return

    missing = sorted(REQUIRED_ENTRY_FIELDS - entry.keys())
    if missing:
        errors.append(f"{label}: missing fields: {', '.join(missing)}")

    if entry.get("status") not in registry["allowed_statuses"]:
        errors.append(f"{label}: invalid status {entry.get('status')!r}")
    if expected_status is not None and entry.get("status") != expected_status:
        errors.append(
            f"{label}: status {entry.get('status')!r} does not match folder "
            f"(expected {expected_status!r})"
        )
    if entry.get("risk_level") not in registry["allowed_risk_levels"]:
        errors.append(f"{label}: invalid risk level {entry.get('risk_level')!r}")
    if entry.get("artifact_type") not in registry["allowed_artifact_types"]:
        errors.append(f"{label}: invalid artifact type {entry.get('artifact_type')!r}")
    if not is_valid_public_url(entry.get("source")):
        errors.append(f"{label}: source must be a public https URL without embedded credentials")

    non_empty_string_fields = (
        "id",
        "name",
        "category",
        "summary",
        "compatibility_notes",
        "safe_usage_boundary",
        "next_action",
    )
    for field in non_empty_string_fields:
        if not isinstance(entry.get(field), str) or not entry[field].strip():
            errors.append(f"{label}: {field} must be a non-empty string")
    if isinstance(entry.get("id"), str) and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]):
        errors.append(f"{label}: id must use lowercase kebab-case")

    boolean_fields = (
        "install_allowed",
        "execution_allowed",
        "requires_sandbox",
        "approved_for_project_integration",
    )
    for field in boolean_fields:
        if type(entry.get(field)) is not bool:
            errors.append(f"{label}: {field} must be a boolean")

    details = entry.get("what_it_does")
    if not isinstance(details, dict):
        errors.append(f"{label}: what_it_does must be a mapping")
    else:
        missing_details = sorted(REQUIRED_WHAT_IT_DOES_FIELDS - details.keys())
        if missing_details:
            errors.append(f"{label}: what_it_does missing: {', '.join(missing_details)}")
        if not isinstance(details.get("main_features"), list) or not details.get("main_features"):
            errors.append(f"{label}: what_it_does.main_features must be a non-empty list")

    for field in ("useful_for", "not_recommended_for", "risk_reasons"):
        if not isinstance(entry.get(field), list) or not entry.get(field):
            errors.append(f"{label}: {field} must be a non-empty list")

    compatibility = entry.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append(f"{label}: compatibility must be a mapping")
    else:
        expected_targets = set(registry["ai_targets"]) | {"other"}
        missing_targets = sorted(expected_targets - compatibility.keys())
        extra_targets = sorted(compatibility.keys() - expected_targets)
        if missing_targets:
            errors.append(f"{label}: compatibility missing: {', '.join(missing_targets)}")
        if extra_targets:
            errors.append(f"{label}: unknown compatibility targets: {', '.join(extra_targets)}")
        for target in registry["ai_targets"]:
            value = compatibility.get(target)
            if value not in registry["allowed_compatibility_values"]:
                errors.append(f"{label}: invalid compatibility {target}={value!r}")
        if not isinstance(compatibility.get("other"), list):
            errors.append(f"{label}: compatibility.other must be a list")
        elif not all(isinstance(value, str) and value.strip() for value in compatibility["other"]):
            errors.append(f"{label}: compatibility.other values must be non-empty strings")

    data_access = entry.get("data_access")
    if not isinstance(data_access, dict):
        errors.append(f"{label}: data_access must be a mapping")
    else:
        missing_access = sorted(REQUIRED_DATA_ACCESS_FIELDS - data_access.keys())
        if missing_access:
            errors.append(f"{label}: data_access missing: {', '.join(missing_access)}")
        extra_access = sorted(data_access.keys() - REQUIRED_DATA_ACCESS_FIELDS)
        if extra_access:
            errors.append(f"{label}: unknown data_access fields: {', '.join(extra_access)}")
        for key, value in data_access.items():
            if key in REQUIRED_DATA_ACCESS_FIELDS and value not in ALLOWED_DATA_ACCESS_VALUES:
                errors.append(f"{label}: invalid data_access {key}={value!r}")

    review = entry.get("review")
    if not isinstance(review, dict):
        errors.append(f"{label}: review must be a mapping")
    else:
        missing_review = sorted(REQUIRED_REVIEW_FIELDS - review.keys())
        if missing_review:
            errors.append(f"{label}: review missing: {', '.join(missing_review)}")
        if not isinstance(review.get("evidence_checked"), list):
            errors.append(f"{label}: review.evidence_checked must be a list")


def check_registry(
    registry: Any, entries_by_path: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    if not isinstance(registry, dict):
        errors.append("skills/registry.yml: top level must be a mapping")
        return
    required = {
        "schema_version",
        "repository_policy",
        "last_updated",
        "allowed_statuses",
        "allowed_risk_levels",
        "allowed_compatibility_values",
        "allowed_artifact_types",
        "ai_targets",
        "default_rules",
        "skills",
    }
    missing = sorted(required - registry.keys())
    if missing:
        errors.append(f"skills/registry.yml: missing fields: {', '.join(missing)}")
        return
    if not isinstance(registry.get("skills"), list):
        errors.append("skills/registry.yml: skills must be a list")
        return

    registry_entries = registry["skills"]
    for index, item in enumerate(registry_entries):
        label = f"skills/registry.yml: skills[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        compact_fields = (
            "id",
            "name",
            "source",
            "registry_file",
            "status",
            "artifact_type",
            "category",
            "summary",
            "risk_level",
        )
        for field in compact_fields:
            if field not in item:
                errors.append(f"{label} missing {field}")
        registry_file = item.get("registry_file")
        if isinstance(registry_file, str):
            registry_path = Path(registry_file)
            if registry_path.is_absolute() or ".." in registry_path.parts:
                errors.append(f"{label} registry_file must stay within the repository")

    for field in ("id", "source", "registry_file"):
        values = [item.get(field) for item in registry_entries if isinstance(item, dict)]
        duplicates = sorted(value for value, count in Counter(values).items() if value and count > 1)
        if duplicates:
            errors.append(f"skills/registry.yml: duplicate {field}: {', '.join(duplicates)}")

    registry_paths = {
        item.get("registry_file") for item in registry_entries if isinstance(item, dict)
    }
    entry_paths_set = set(entries_by_path)
    for registry_path in sorted(path for path in registry_paths if isinstance(path, str)):
        full_path = ROOT / registry_path
        if not full_path.is_file():
            errors.append(f"skills/registry.yml: missing registry_file {registry_path}")
            continue
        profile = entries_by_path.get(registry_path)
        registry_item = next(item for item in registry_entries if item.get("registry_file") == registry_path)
        if profile:
            for field in ("id", "name", "source", "status", "artifact_type", "category", "risk_level"):
                if registry_item.get(field) != profile.get(field):
                    errors.append(
                        f"skills/registry.yml: {registry_path} has mismatched {field}: "
                        f"{registry_item.get(field)!r} != {profile.get(field)!r}"
                    )
    orphaned = sorted(entry_paths_set - registry_paths)
    if orphaned:
        errors.append(f"skills/registry.yml: orphaned profiles: {', '.join(orphaned)}")

    expected_order = sorted(
        registry_entries,
        key=lambda item: (
            item.get("status") == "rejected",
            registry["allowed_artifact_types"].index(item.get("artifact_type"))
            if item.get("artifact_type") in registry["allowed_artifact_types"]
            else len(registry["allowed_artifact_types"]),
            str(item.get("name", "")).casefold(),
        ),
    )
    if registry_entries != expected_order:
        errors.append("skills/registry.yml: entries are not in the documented predictable order")


def github_anchor(heading: str) -> str:
    anchor = heading.strip().lower()
    anchor = re.sub(r"[^\w\- ]", "", anchor, flags=re.UNICODE)
    return re.sub(r"[ _]+", "-", anchor)


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = github_anchor(match.group(1))
        suffix = f"-{counts[base]}" if counts[base] else ""
        anchors.add(base + suffix)
        counts[base] += 1
    return anchors


def check_internal_links(errors: list[str], root: Path = ROOT) -> None:
    for path in sorted(root.rglob("*.md")):
        if IGNORED_DIRECTORY_NAMES.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw_target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            if not raw_target or raw_target.startswith(("https://", "http://", "mailto:")):
                continue
            file_part, separator, fragment = raw_target.partition("#")
            target = path if not file_part else (path.parent / file_part).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(root)}: link escapes repository: {raw_target}")
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: broken internal link: {raw_target}")
                continue
            if separator and target.suffix.lower() == ".md" and fragment:
                if fragment not in markdown_anchors(target):
                    errors.append(f"{path.relative_to(root)}: missing anchor: {raw_target}")


def check_secrets(errors: list[str], root: Path = ROOT) -> None:
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or IGNORED_DIRECTORY_NAMES.intersection(path.parts)
        ):
            continue
        if path.is_symlink():
            errors.append(f"{path.relative_to(root)}: symbolic links are not allowed in catalog content")
            continue
        if path.name == ".env" or path.name.startswith(".env."):
            errors.append(f"{path.relative_to(root)}: environment files must not be committed")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(root)}:{line}: possible {name}")


def profile_link(registry_file: str) -> str:
    return f"../{registry_file}"


def render_grouped_index(
    title: str,
    description: str,
    groups: list[str],
    entries: list[dict[str, Any]],
    group_field: str,
) -> str:
    lines = [f"# {title}", "", description, ""]
    for group in groups:
        grouped = [entry for entry in entries if entry.get(group_field) == group]
        if not grouped:
            continue
        lines.extend([f"## `{group}`", "", "| Entry | Type | Status | Risk |", "| --- | --- | --- | --- |"])
        for entry in sorted(grouped, key=lambda item: item["name"].casefold()):
            link = profile_link(entry["registry_file"])
            lines.append(
                f"| [{entry['name']}]({link}) | `{entry['artifact_type']}` | "
                f"`{entry['status']}` | `{entry['risk_level']}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_indexes(registry: dict[str, Any]) -> dict[str, str]:
    entries = registry["skills"]
    category_groups = sorted({entry["category"] for entry in entries})
    rendered = {
        "category": render_grouped_index(
            "Catalog by category",
            "Compact category view generated from `skills/registry.yml`.",
            category_groups,
            entries,
            "category",
        ),
        "status": render_grouped_index(
            "Catalog by status",
            "Status describes review maturity, not installation safety.",
            registry["allowed_statuses"],
            entries,
            "status",
        ),
        "risk": render_grouped_index(
            "Catalog by risk",
            "Risk levels are documentary assessments and can change when evidence changes.",
            registry["allowed_risk_levels"],
            entries,
            "risk_level",
        ),
    }

    lines = [
        "# Catalog by compatibility",
        "",
        "Compatibility describes documented applicability; it does not authorize installation or execution.",
        "",
        "| Entry | "
        + " | ".join(target.replace("_", " ").title() for target in registry["ai_targets"])
        + " |",
        "| --- | " + " | ".join("---" for _ in registry["ai_targets"]) + " |",
    ]
    for entry in entries:
        profile = load_yaml(ROOT / entry["registry_file"], [])
        compatibility = profile["compatibility"]
        values = " | ".join(f"`{compatibility[target]}`" for target in registry["ai_targets"])
        lines.append(f"| [{entry['name']}]({profile_link(entry['registry_file'])}) | {values} |")
    rendered["compatibility"] = "\n".join(lines) + "\n"
    return rendered


def check_or_write_indexes(
    registry: dict[str, Any], errors: list[str], write_indexes: bool
) -> None:
    rendered = render_indexes(registry)
    for name, path in INDEX_PATHS.items():
        if write_indexes:
            path.write_text(rendered[name], encoding="utf-8")
        elif not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: generated index is missing")
        elif path.read_text(encoding="utf-8") != rendered[name]:
            errors.append(
                f"{path.relative_to(ROOT)}: generated index is stale; "
                "run python scripts/validate_registry.py --write-indexes"
            )


def validate(root: Path = ROOT, write_indexes: bool = False) -> list[str]:
    global ROOT, REGISTRY_PATH, INDEX_PATHS
    original_values = ROOT, REGISTRY_PATH, INDEX_PATHS
    if root != ROOT:
        ROOT = root.resolve()
        REGISTRY_PATH = ROOT / "skills" / "registry.yml"
        INDEX_PATHS = {
            "category": ROOT / "docs" / "catalog_by_category.md",
            "compatibility": ROOT / "docs" / "catalog_by_compatibility.md",
            "status": ROOT / "docs" / "catalog_by_status.md",
            "risk": ROOT / "docs" / "catalog_by_risk.md",
        }
    errors: list[str] = []
    try:
        registry = load_yaml(REGISTRY_PATH, errors)
        if not isinstance(registry, dict):
            return errors

        entries_by_path: dict[str, dict[str, Any]] = {}
        ids: list[str] = []
        sources: list[str] = []
        for path in entry_paths(ROOT):
            entry = load_yaml(path, errors)
            if isinstance(entry, dict):
                relative = str(path.relative_to(ROOT))
                entries_by_path[relative] = entry
                ids.append(str(entry.get("id")))
                sources.append(str(entry.get("source")))
                check_entry(path, entry, registry, errors, ENTRY_DIRECTORIES[path.parent.name])

        template_path = ROOT / "skills" / "profile-template.yml"
        template = load_yaml(template_path, errors)
        if template is not None:
            check_entry(template_path, template, registry, errors, "candidate")

        for field, values in (("id", ids), ("source", sources)):
            duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
            if duplicates:
                errors.append(f"profiles: duplicate {field}: {', '.join(duplicates)}")

        check_registry(registry, entries_by_path, errors)
        if not errors:
            check_or_write_indexes(registry, errors, write_indexes)
        check_internal_links(errors, ROOT)
        check_secrets(errors, ROOT)
        return errors
    finally:
        ROOT, REGISTRY_PATH, INDEX_PATHS = original_values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-indexes",
        action="store_true",
        help="regenerate the four Markdown catalog indexes before validation",
    )
    args = parser.parse_args()
    errors = validate(write_indexes=args.write_indexes)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Registry validation passed: YAML, schema, profiles, indexes, links, and secret patterns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
