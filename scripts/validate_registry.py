#!/usr/bin/env python3
"""Validate the documentation-only AI catalog without making network requests."""

from __future__ import annotations

import argparse
import html
import ipaddress
import re
import sys
import xml.etree.ElementTree as ElementTree
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath
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
PROFILE_SUFFIXES = {".yml", ".yaml"}
REGISTRY_REQUIRED_FIELDS = {
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
REGISTRY_VOCABULARY_FIELDS = (
    "allowed_statuses",
    "allowed_risk_levels",
    "allowed_compatibility_values",
    "allowed_artifact_types",
    "ai_targets",
)
REQUIRED_ENTRY_FIELDS = {
    "id",
    "name",
    "source",
    "status",
    "artifact_type",
    "category",
    "source_owner",
    "content_languages",
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
    "automatic_commits",
    "browser_control",
    "modifies_behavior",
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
DECLARED_CAPABILITY_VALUES = {"yes", "likely", "possible"}
RISK_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
CAPABILITY_RISK_FLOORS = {
    "medium": {
        "local_files",
        "network",
        "persistent_memory",
        "writes_files",
        "modifies_behavior",
    },
    "high": {
        "shell_commands",
        "git_hooks",
        "modifies_code",
        "credentials",
        "browser_control",
        "automatic_commits",
    },
}
HIGH_CONTROL_BOOLEAN_FIELDS = {
    "install_allowed",
    "execution_allowed",
    "approved_for_project_integration",
}
ISSUE_FORM_TYPES = {"checkboxes", "dropdown", "input", "markdown", "textarea", "upload"}
ISSUE_FORM_ID_RE = re.compile(r"[A-Za-z0-9_-]+")
AI_TARGET_DISPLAY_NAMES = {
    "chatgpt": "ChatGPT",
    "openai_codex": "OpenAI Codex",
    "claude": "Claude",
    "claude_code": "Claude Code",
    "perplexity": "Perplexity",
    "gemini": "Gemini",
    "cursor": "Cursor",
    "windsurf": "Windsurf",
}
INDEX_PATHS = {
    "category": ROOT / "docs" / "catalog_by_category.md",
    "use_case": ROOT / "docs" / "catalog_by_use_case.md",
    "company": ROOT / "docs" / "catalog_by_company.md",
    "ai": ROOT / "docs" / "catalog_by_ai.md",
    "status": ROOT / "docs" / "catalog_by_status.md",
    "risk": ROOT / "docs" / "catalog_by_risk.md",
    "language": ROOT / "docs" / "catalog_by_language.md",
    "recent": ROOT / "docs" / "catalog_recent_reviews.md",
}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r"(?:href|src)=['\"]([^'\"]+)['\"]", re.I)
HTML_TAG_RE = re.compile(r"<[A-Za-z][^<>]*>", re.DOTALL)
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
        directory_path = root / "skills" / directory
        paths.extend(
            sorted(
                path
                for path in directory_path.iterdir()
                if path.suffix.casefold() in PROFILE_SUFFIXES
            )
            if directory_path.is_dir()
            else []
        )
    return paths


def normalize_registry_schema(registry: Any, errors: list[str]) -> dict[str, Any] | None:
    """Validate registry structure and return a safe, normalized copy for later checks."""
    label = "skills/registry.yml"
    if not isinstance(registry, dict):
        errors.append(f"{label}: top level must be a mapping")
        return None

    missing = sorted(REGISTRY_REQUIRED_FIELDS - registry.keys())
    if missing:
        errors.append(f"{label}: missing fields: {', '.join(missing)}")
    unexpected = sorted(
        (key for key in registry if key not in REGISTRY_REQUIRED_FIELDS),
        key=str,
    )
    if unexpected:
        errors.append(f"{label}: unknown fields: {', '.join(map(str, unexpected))}")

    if type(registry.get("schema_version")) is not int:
        errors.append(f"{label}: schema_version must be an integer")
    for field in ("repository_policy", "last_updated"):
        if not isinstance(registry.get(field), str) or not registry[field].strip():
            errors.append(f"{label}: {field} must be a non-empty string")
    if not isinstance(registry.get("default_rules"), dict):
        errors.append(f"{label}: default_rules must be a mapping")
    if not isinstance(registry.get("skills"), list):
        errors.append(f"{label}: skills must be a list")

    normalized = dict(registry)
    vocabularies_are_usable = True
    for field in REGISTRY_VOCABULARY_FIELDS:
        values = registry.get(field)
        if not isinstance(values, list):
            errors.append(f"{label}: {field} must be a list")
            vocabularies_are_usable = False
            continue
        if not values:
            errors.append(f"{label}: {field} must not be empty")
            vocabularies_are_usable = False
            continue
        if not all(isinstance(value, str) and value.strip() for value in values):
            errors.append(f"{label}: {field} values must be non-empty strings")
            vocabularies_are_usable = False
            continue
        duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
        if duplicates:
            errors.append(f"{label}: duplicate {field} values: {', '.join(duplicates)}")
            vocabularies_are_usable = False
            continue
        if field == "allowed_risk_levels" and values != list(RISK_RANK):
            errors.append(
                f"{label}: allowed_risk_levels must be ordered as: {', '.join(RISK_RANK)}"
            )
            vocabularies_are_usable = False
            continue
        normalized[field] = tuple(values)

    if missing or unexpected or not vocabularies_are_usable:
        return None
    if (
        type(registry.get("schema_version")) is not int
        or not all(
            isinstance(registry.get(field), str) and registry[field].strip()
            for field in ("repository_policy", "last_updated")
        )
        or not isinstance(registry.get("default_rules"), dict)
        or not isinstance(registry.get("skills"), list)
    ):
        return None
    return normalized


def normalize_registry_file(value: Any) -> str | None:
    """Return a canonical admitted profile path, or None for an unsafe/invalid path."""
    if not isinstance(value, str) or not value.strip() or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        return None
    if len(path.parts) != 3 or path.parts[0] != "skills":
        return None
    if path.parts[1] not in ENTRY_DIRECTORIES:
        return None
    if path.suffix.casefold() not in PROFILE_SUFFIXES:
        return None
    normalized = path.as_posix()
    return normalized if normalized == value else None


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
) -> bool:
    initial_error_count = len(errors)
    label = str(path.relative_to(ROOT))
    if not isinstance(entry, dict):
        errors.append(f"{label}: top level must be a mapping")
        return False

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
        "source_owner",
        "summary",
        "compatibility_notes",
        "safe_usage_boundary",
        "next_action",
    )
    for field in non_empty_string_fields:
        if not isinstance(entry.get(field), str) or not entry[field].strip():
            errors.append(f"{label}: {field} must be a non-empty string")
    languages = entry.get("content_languages")
    if not isinstance(languages, list) or not languages:
        errors.append(f"{label}: content_languages must be a non-empty list")
    elif not all(isinstance(value, str) and value.strip() for value in languages):
        errors.append(f"{label}: content_languages values must be non-empty strings")
    else:
        duplicate_languages = sorted(
            value for value, count in Counter(languages).items() if count > 1
        )
        if duplicate_languages:
            errors.append(
                f"{label}: duplicate content_languages values: "
                + ", ".join(duplicate_languages)
            )
    if isinstance(entry.get("id"), str) and not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]
    ):
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
        elif not all(isinstance(value, str) and value.strip() for value in entry[field]):
            errors.append(f"{label}: {field} values must be non-empty strings")
        else:
            duplicate_values = sorted(
                value for value, count in Counter(entry[field]).items() if count > 1
            )
            if duplicate_values:
                errors.append(
                    f"{label}: duplicate {field} values: {', '.join(duplicate_values)}"
                )

    compatibility = entry.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append(f"{label}: compatibility must be a mapping")
    else:
        expected_targets = set(registry["ai_targets"]) | {"other"}
        missing_targets = sorted(expected_targets - compatibility.keys())
        extra_targets = sorted(
            (key for key in compatibility if key not in expected_targets),
            key=str,
        )
        if missing_targets:
            errors.append(f"{label}: compatibility missing: {', '.join(missing_targets)}")
        if extra_targets:
            errors.append(
                f"{label}: unknown compatibility targets: {', '.join(map(str, extra_targets))}"
            )
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
        extra_access = sorted(
            (key for key in data_access if key not in REQUIRED_DATA_ACCESS_FIELDS),
            key=str,
        )
        if extra_access:
            errors.append(
                f"{label}: unknown data_access fields: {', '.join(map(str, extra_access))}"
            )
        for key, value in data_access.items():
            if key in REQUIRED_DATA_ACCESS_FIELDS and value not in ALLOWED_DATA_ACCESS_VALUES:
                errors.append(f"{label}: invalid data_access {key}={value!r}")

        risk_level = entry.get("risk_level")
        if risk_level in RISK_RANK:
            for minimum, capabilities in CAPABILITY_RISK_FLOORS.items():
                declared = sorted(
                    capability
                    for capability in capabilities
                    if data_access.get(capability) in DECLARED_CAPABILITY_VALUES
                )
                if declared and RISK_RANK[risk_level] < RISK_RANK[minimum]:
                    errors.append(
                        f"{label}: risk level {risk_level!r} is below minimum {minimum!r} "
                        f"for declared capabilities: {', '.join(declared)}"
                    )
            enabled_controls = sorted(
                field for field in HIGH_CONTROL_BOOLEAN_FIELDS if entry.get(field) is True
            )
            if enabled_controls and RISK_RANK[risk_level] < RISK_RANK["high"]:
                errors.append(
                    f"{label}: risk level {risk_level!r} is below minimum 'high' "
                    f"for enabled controls: {', '.join(enabled_controls)}"
                )

    review = entry.get("review")
    if not isinstance(review, dict):
        errors.append(f"{label}: review must be a mapping")
    else:
        missing_review = sorted(REQUIRED_REVIEW_FIELDS - review.keys())
        if missing_review:
            errors.append(f"{label}: review missing: {', '.join(missing_review)}")
        reviewed_at = review.get("reviewed_at")
        if reviewed_at is not None:
            if not isinstance(reviewed_at, str) or re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", reviewed_at
            ) is None:
                errors.append(
                    f"{label}: review.reviewed_at must be null or an ISO YYYY-MM-DD date"
                )
            else:
                try:
                    date.fromisoformat(reviewed_at)
                except ValueError:
                    errors.append(
                        f"{label}: review.reviewed_at must be null or a real ISO date"
                    )
        if not isinstance(review.get("evidence_checked"), list):
            errors.append(f"{label}: review.evidence_checked must be a list")
    return len(errors) == initial_error_count


def check_registry(
    registry: dict[str, Any],
    entries_by_path: dict[str, dict[str, Any]],
    valid_profile_paths: set[str],
    errors: list[str],
) -> None:
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
            elif not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{label} {field} must be a non-empty string")
        registry_file = item.get("registry_file")
        if normalize_registry_file(registry_file) is None:
            errors.append(
                f"{label} registry_file must be a canonical YAML profile in "
                "skills/candidates, skills/accepted, skills/watchlist, or skills/rejected"
            )

    for field in ("id", "source", "registry_file"):
        values = [
            item.get(field)
            for item in registry_entries
            if isinstance(item, dict) and isinstance(item.get(field), str)
        ]
        duplicates = sorted(
            value for value, count in Counter(values).items() if value and count > 1
        )
        if duplicates:
            errors.append(f"skills/registry.yml: duplicate {field}: {', '.join(duplicates)}")

    registry_paths = {
        item.get("registry_file")
        for item in registry_entries
        if isinstance(item, dict) and isinstance(item.get("registry_file"), str)
    }
    entry_paths_set = set(entries_by_path)
    unadmitted = sorted(registry_paths - entry_paths_set)
    if unadmitted:
        errors.append(
            "skills/registry.yml: registered paths are not admitted profiles: "
            + ", ".join(unadmitted)
        )
    for registry_path in sorted(registry_paths & entry_paths_set):
        full_path = ROOT / registry_path
        if full_path.is_symlink():
            errors.append(f"skills/registry.yml: registry_file is a symbolic link: {registry_path}")
            continue
        profile = entries_by_path.get(registry_path)
        registry_item = next(
            item
            for item in registry_entries
            if isinstance(item, dict) and item.get("registry_file") == registry_path
        )
        if registry_path not in valid_profile_paths:
            errors.append(
                "skills/registry.yml: registry_file is not a complete valid profile: "
                f"{registry_path}"
            )
        elif profile:
            compared_fields = (
                "id",
                "name",
                "source",
                "status",
                "artifact_type",
                "category",
                "risk_level",
            )
            for field in compared_fields:
                if registry_item.get(field) != profile.get(field):
                    errors.append(
                        f"skills/registry.yml: {registry_path} has mismatched {field}: "
                        f"{registry_item.get(field)!r} != {profile.get(field)!r}"
                    )
    orphaned = sorted(entry_paths_set - registry_paths)
    if orphaned:
        errors.append(f"skills/registry.yml: orphaned profiles: {', '.join(orphaned)}")

    mapping_entries = [item for item in registry_entries if isinstance(item, dict)]
    expected_order = sorted(
        mapping_entries,
        key=lambda item: (
            item.get("status") == "rejected",
            registry["allowed_artifact_types"].index(item.get("artifact_type"))
            if item.get("artifact_type") in registry["allowed_artifact_types"]
            else len(registry["allowed_artifact_types"]),
            str(item.get("name", "")).casefold(),
        ),
    )
    if len(mapping_entries) == len(registry_entries) and registry_entries != expected_order:
        errors.append("skills/registry.yml: entries are not in the documented predictable order")


def github_anchor(heading: str) -> str:
    anchor = heading.strip().lower()
    anchor = re.sub(r"[^\w\- ]", "", anchor, flags=re.UNICODE)
    return re.sub(r"[ _]+", "-", anchor)


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: Counter[str] = Counter()
    text = path.read_text(encoding="utf-8")
    masked_text, _ = mask_html_comments(text)
    lines = masked_text.splitlines()
    fenced_lines, _ = fenced_markdown_line_numbers(lines)
    for index in range(len(lines)):
        heading = markdown_heading_at(lines, index, fenced_lines)
        if heading is None:
            continue
        _, heading_text = heading
        base = github_anchor(heading_text)
        suffix = f"-{counts[base]}" if counts[base] else ""
        anchors.add(base + suffix)
        counts[base] += 1
    return anchors


def check_all_yaml(errors: list[str], root: Path = ROOT) -> None:
    paths = sorted({*root.rglob("*.yml"), *root.rglob("*.yaml")})
    for path in paths:
        if IGNORED_DIRECTORY_NAMES.intersection(path.parts):
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(root)}: invalid YAML: {exc}")


def check_issue_forms(errors: list[str], root: Path = ROOT) -> None:
    forms_directory = root / ".github" / "ISSUE_TEMPLATE"
    if not forms_directory.is_dir():
        errors.append(".github/ISSUE_TEMPLATE: issue form directory is missing")
        return

    for path in sorted(forms_directory.glob("*.yaml")):
        errors.append(
            f"{path.relative_to(root)}: GitHub issue forms must use the .yml extension"
        )

    names: list[str] = []
    for path in sorted(forms_directory.glob("*.yml")):
        if path.name == "config.yml":
            continue
        relative = path.relative_to(root)
        try:
            form = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            continue
        if not isinstance(form, dict):
            errors.append(f"{relative}: issue form must be a mapping")
            continue
        allowed_top_level = {
            "name",
            "description",
            "title",
            "labels",
            "assignees",
            "type",
            "projects",
            "body",
        }
        missing = sorted({"name", "description", "title", "body"} - form.keys())
        if missing:
            errors.append(f"{relative}: issue form missing: {', '.join(missing)}")
            continue
        unexpected = sorted(form.keys() - allowed_top_level, key=str)
        if unexpected:
            errors.append(
                f"{relative}: unsupported top-level keys: {', '.join(map(str, unexpected))}"
            )
        for field in ("name", "description"):
            if not isinstance(form.get(field), str) or not form[field].strip():
                errors.append(f"{relative}: {field} must be a non-empty string")
        if isinstance(form.get("name"), str):
            names.append(form["name"])
            if len(form["name"].strip()) <= 3:
                errors.append(f"{relative}: name must contain more than three characters")
        if not isinstance(form.get("title"), str):
            errors.append(f"{relative}: title must be a string")
        if not isinstance(form["body"], list) or not form["body"]:
            errors.append(f"{relative}: issue form body must be a non-empty list")
            continue
        ids: list[str] = []
        for index, item in enumerate(form["body"]):
            if not isinstance(item, dict) or "type" not in item or "attributes" not in item:
                errors.append(f"{relative}: body item {index} is missing type or attributes")
                continue
            item_type = item["type"]
            if not isinstance(item_type, str) or item_type not in ISSUE_FORM_TYPES:
                errors.append(f"{relative}: body item {index} has unsupported type {item_type!r}")
                continue
            attributes = item["attributes"]
            if not isinstance(attributes, dict):
                errors.append(f"{relative}: body item {index} attributes must be a mapping")
                continue
            if item_type == "markdown":
                if "id" in item:
                    errors.append(f"{relative}: markdown body item {index} must not define an id")
                if not isinstance(attributes.get("value"), str) or not attributes["value"].strip():
                    errors.append(
                        f"{relative}: markdown body item {index} requires a non-empty value"
                    )
                continue

            if not isinstance(item.get("id"), str) or not item["id"].strip():
                errors.append(f"{relative}: body item {index} requires a non-empty id")
            elif ISSUE_FORM_ID_RE.fullmatch(item["id"]) is None:
                errors.append(
                    f"{relative}: body item {index} id may use only letters, numbers, -, and _"
                )
            else:
                ids.append(item["id"])
            if not isinstance(attributes.get("label"), str) or not attributes["label"].strip():
                errors.append(f"{relative}: body item {index} requires a non-empty label")

            validations = item.get("validations")
            if validations is not None:
                if not isinstance(validations, dict):
                    errors.append(f"{relative}: body item {index} validations must be a mapping")
                elif "required" in validations and type(validations["required"]) is not bool:
                    errors.append(
                        f"{relative}: body item {index} validations.required must be a boolean"
                    )

            if item_type == "dropdown":
                options = attributes.get("options")
                if (
                    not isinstance(options, list)
                    or not options
                    or not all(isinstance(option, str) and option.strip() for option in options)
                ):
                    errors.append(
                        f"{relative}: dropdown body item {index} requires non-empty string options"
                    )
                elif len(options) != len(set(options)):
                    errors.append(f"{relative}: dropdown body item {index} options must be unique")
                if "multiple" in attributes and type(attributes["multiple"]) is not bool:
                    errors.append(
                        f"{relative}: dropdown body item {index} multiple must be a boolean"
                    )
                default = attributes.get("default")
                if default is not None and (
                    type(default) is not int
                    or not isinstance(options, list)
                    or default < 0
                    or default >= len(options)
                ):
                    errors.append(
                        f"{relative}: dropdown body item {index} default must index an option"
                    )

            if item_type == "checkboxes":
                options = attributes.get("options")
                if not isinstance(options, list) or not options:
                    errors.append(
                        f"{relative}: checkboxes body item {index} requires a non-empty options list"
                    )
                else:
                    for option_index, option in enumerate(options):
                        if not isinstance(option, dict):
                            errors.append(
                                f"{relative}: checkbox option {index}.{option_index} must be a mapping"
                            )
                            continue
                        if not isinstance(option.get("label"), str) or not option["label"].strip():
                            errors.append(
                                f"{relative}: checkbox option {index}.{option_index} requires a label"
                            )
                        if "required" in option and type(option["required"]) is not bool:
                            errors.append(
                                f"{relative}: checkbox option {index}.{option_index} required must be a boolean"
                            )
        duplicates = sorted(value for value, count in Counter(ids).items() if count > 1)
        if duplicates:
            errors.append(f"{relative}: duplicate body ids: {', '.join(duplicates)}")

    duplicate_names = sorted(value for value, count in Counter(names).items() if count > 1)
    if duplicate_names:
        errors.append(f".github/ISSUE_TEMPLATE: duplicate form names: {', '.join(duplicate_names)}")

    config_path = forms_directory / "config.yml"
    if not config_path.is_file():
        errors.append(".github/ISSUE_TEMPLATE/config.yml: template chooser config is missing")
        return
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return
    if not isinstance(config, dict):
        errors.append(".github/ISSUE_TEMPLATE/config.yml: config must be a mapping")
        return
    missing_config = sorted({"blank_issues_enabled", "contact_links"} - config.keys())
    if missing_config:
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: missing: " + ", ".join(missing_config)
        )
    unexpected_config = sorted(
        config.keys() - {"blank_issues_enabled", "contact_links"}, key=str
    )
    if unexpected_config:
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: unsupported keys: "
            + ", ".join(map(str, unexpected_config))
        )
    if type(config.get("blank_issues_enabled")) is not bool:
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: blank_issues_enabled must be a boolean"
        )
    contact_links = config.get("contact_links")
    if not isinstance(contact_links, list) or not contact_links:
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: contact_links must be a non-empty list"
        )
    else:
        for index, contact in enumerate(contact_links):
            label = f".github/ISSUE_TEMPLATE/config.yml: contact_links[{index}]"
            if not isinstance(contact, dict):
                errors.append(f"{label} must be a mapping")
                continue
            missing_contact = sorted({"name", "url", "about"} - contact.keys())
            if missing_contact:
                errors.append(f"{label} missing: {', '.join(missing_contact)}")
            for field in ("name", "about"):
                if not isinstance(contact.get(field), str) or not contact[field].strip():
                    errors.append(f"{label} {field} must be a non-empty string")
            if not is_valid_public_url(contact.get("url")):
                errors.append(f"{label} url must be a public HTTPS URL")


def check_svg_files(errors: list[str], root: Path = ROOT) -> None:
    for path in sorted(root.rglob("*.svg")):
        if IGNORED_DIRECTORY_NAMES.intersection(path.parts):
            continue
        try:
            ElementTree.parse(path)
        except (OSError, ElementTree.ParseError) as exc:
            errors.append(f"{path.relative_to(root)}: invalid SVG/XML: {exc}")


def mask_html_comments(text: str) -> tuple[str, set[int]]:
    """Mask HTML comments while preserving line positions for Markdown checks."""
    comment_lines: set[int] = set()

    def replace_comment(match: re.Match[str]) -> str:
        start_line = text.count("\n", 0, match.start()) + 1
        end_line = start_line + match.group().count("\n")
        comment_lines.update(range(start_line, end_line + 1))
        return re.sub(r"[^\n]", " ", match.group())

    return re.sub(r"<!--.*?-->", replace_comment, text, flags=re.DOTALL), comment_lines


def fenced_markdown_line_numbers(lines: list[str]) -> tuple[set[int], bool]:
    """Return one-based fenced line numbers and whether the final fence is unclosed."""
    fenced_lines: set[int] = set()
    in_fence = False
    fence_character = ""
    fence_length = 0
    for line_number, line in enumerate(lines, start=1):
        indentation = len(line) - len(line.lstrip(" "))
        fence_match = (
            re.match(r"^(`{3,}|~{3,})(.*)$", line.lstrip(" "))
            if indentation <= 3
            else None
        )
        if in_fence:
            fenced_lines.add(line_number)
            if fence_match:
                marker = fence_match.group(1)
                remainder = fence_match.group(2)
                if (
                    marker[0] == fence_character
                    and len(marker) >= fence_length
                    and not remainder.strip()
                ):
                    in_fence = False
                    fence_character = ""
                    fence_length = 0
            continue
        if fence_match:
            marker = fence_match.group(1)
            fenced_lines.add(line_number)
            in_fence = True
            fence_character = marker[0]
            fence_length = len(marker)
    return fenced_lines, in_fence


def is_setext_title_line(line: str) -> bool:
    """Return whether a visible line can be paragraph text for a Setext heading."""
    indentation = len(line) - len(line.lstrip(" "))
    if indentation > 3 or not line.strip():
        return False
    block_starts = (
        r"^ {0,3}#{1,6}(?:\s+|$)",
        r"^ {0,3}>",
        r"^ {0,3}(?:[-+*]|\d{1,9}[.)])\s+",
        r"^ {0,3}(?:`{3,}|~{3,})",
        r"^ {0,3}<",
        r"^ {0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$",
    )
    return not any(re.match(pattern, line) for pattern in block_starts)


def markdown_heading_at(
    lines: list[str], index: int, fenced_lines: set[int]
) -> tuple[int, str] | None:
    """Return a CommonMark ATX or Setext heading at a zero-based line index."""
    line_number = index + 1
    if line_number in fenced_lines:
        return None
    line = lines[index]
    atx = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
    if atx:
        return len(atx.group(1)), atx.group(2)
    setext = re.match(r"^ {0,3}(=+|-+)\s*$", line)
    previous_line_number = line_number - 1
    if (
        setext
        and previous_line_number >= 1
        and previous_line_number not in fenced_lines
        and is_setext_title_line(lines[index - 1])
    ):
        return (1 if setext.group(1).startswith("=") else 2), lines[index - 1].strip()
    return None


def check_markdown_format(errors: list[str], root: Path = ROOT) -> None:
    h1_optional = {Path(".github/pull_request_template.md")}
    for path in sorted(root.rglob("*.md")):
        if IGNORED_DIRECTORY_NAMES.intersection(path.parts):
            continue
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        raw_lines = text.splitlines()
        masked_text, comment_lines = mask_html_comments(text)
        lines = masked_text.splitlines()
        if not text.strip():
            errors.append(f"{relative}: Markdown file is empty")
            continue
        fenced_lines, has_unclosed_fence = fenced_markdown_line_numbers(lines)
        h1_count = 0
        previous_level = 0
        blank_run = 0
        for index, line in enumerate(lines):
            line_number = index + 1
            if line_number in fenced_lines or (
                line_number in comment_lines and not line.strip()
            ):
                blank_run = 0
                continue
            raw_line = raw_lines[line_number - 1]
            if not raw_line.strip():
                blank_run += 1
                if blank_run > 2:
                    errors.append(
                        f"{relative}:{line_number}: more than two consecutive blank lines"
                    )
            else:
                blank_run = 0
            heading = markdown_heading_at(lines, index, fenced_lines)
            if heading is None:
                continue
            level, _ = heading
            if level == 1:
                h1_count += 1
            if previous_level and level > previous_level + 1:
                errors.append(
                    f"{relative}:{line_number}: heading level jumps from "
                    f"{previous_level} to {level}"
                )
            previous_level = level
        if relative not in h1_optional and h1_count != 1:
            errors.append(f"{relative}: expected exactly one level-one heading, found {h1_count}")
        if has_unclosed_fence:
            errors.append(f"{relative}: unclosed fenced code block")
        visible_text = "\n".join(
            "" if line_number in fenced_lines else line
            for line_number, line in enumerate(lines, start=1)
        )
        if re.search(r"!\[\]\(", strip_inline_code_spans(visible_text)):
            errors.append(f"{relative}: Markdown images must have alternative text")


def strip_inline_code_spans(text: str) -> str:
    """Remove CommonMark-style backtick spans before interpreting example markup."""
    runs = []
    for match in re.finditer(r"`+", text):
        backslash_count = 0
        position = match.start() - 1
        while position >= 0 and text[position] == "\\":
            backslash_count += 1
            position -= 1
        if backslash_count % 2 == 0:
            runs.append(match)
    output: list[str] = []
    cursor = 0
    run_index = 0
    while run_index < len(runs):
        opener = runs[run_index]
        closer_index = next(
            (
                index
                for index in range(run_index + 1, len(runs))
                if len(runs[index].group()) == len(opener.group())
            ),
            None,
        )
        if closer_index is None:
            run_index += 1
            continue
        closer = runs[closer_index]
        output.append(text[cursor : opener.start()])
        cursor = closer.end()
        run_index = closer_index + 1
    output.append(text[cursor:])
    return "".join(output)


def internal_link_targets(text: str) -> list[str]:
    masked_text, _ = mask_html_comments(text)
    lines = masked_text.splitlines()
    fenced_lines, _ = fenced_markdown_line_numbers(lines)
    unfenced_text = "\n".join(
        "" if line_number in fenced_lines else line
        for line_number, line in enumerate(lines, start=1)
    )
    searchable_text = strip_inline_code_spans(unfenced_text)
    markdown_targets = [
        match.group(1) for match in MARKDOWN_LINK_RE.finditer(searchable_text)
    ]
    html_targets = [
        attribute.group(1)
        for tag in HTML_TAG_RE.finditer(searchable_text)
        for attribute in HTML_LINK_RE.finditer(tag.group())
    ]
    return markdown_targets + html_targets


def check_internal_links(errors: list[str], root: Path = ROOT) -> None:
    for path in sorted(root.rglob("*.md")):
        if IGNORED_DIRECTORY_NAMES.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for target_value in internal_link_targets(text):
            raw_target = target_value.strip().split(maxsplit=1)[0].strip("<>")
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
        relative = path.relative_to(root)
        if IGNORED_DIRECTORY_NAMES.intersection(relative.parts[:-1]):
            continue
        if path.is_symlink():
            errors.append(f"{relative}: symbolic links are not allowed in catalog content")
            continue
        if (
            not path.is_file()
            or IGNORED_DIRECTORY_NAMES.intersection(path.parts)
        ):
            continue
        if path.name == ".env" or path.name.startswith(".env."):
            errors.append(f"{relative}: environment files must not be committed")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{relative}:{line}: possible {name}")


def check_readme_catalog_count(
    registry: dict[str, Any], errors: list[str], root: Path = ROOT
) -> None:
    readme = (root / "README.md").read_text(encoding="utf-8")
    expected_badge = f"reviews-{len(registry['skills'])}-blue"
    if expected_badge not in readme:
        errors.append(
            "README.md: reviewed-entry badge is stale; "
            f"expected a badge containing {expected_badge!r}"
        )


def profile_link(registry_file: str) -> str:
    return f"../{registry_file}"


def normalized_table_cell(value: Any) -> str:
    """Normalize line structure shared by plain and code-formatted table cells."""
    return (
        str(value)
        .replace("\r\n", "<br>")
        .replace("\r", "<br>")
        .replace("\n", "<br>")
    )


def markdown_table_cell(value: Any) -> str:
    """Render metadata as plain text without allowing Markdown or HTML injection."""
    escaped_html = normalized_table_cell(html.escape(str(value), quote=False))
    return re.sub(r"([\\`*{}\[\]()!_|])", r"\\\1", escaped_html)


def markdown_table_code_cell(value: Any) -> str:
    """Keep code-style values from breaking their table cell or backtick delimiter."""
    return normalized_table_cell(value).replace("|", r"\|").replace("`", "&#96;")


def render_grouped_index(
    title: str,
    description: str,
    groups: list[str],
    entries: list[dict[str, Any]],
    group_field: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        description,
        "",
        "[Back to the catalog home](../README.md)",
        "",
    ]
    for group in groups:
        grouped = [entry for entry in entries if entry.get(group_field) == group]
        if not grouped:
            continue
        lines.extend(
            [
                f"## `{group}`",
                "",
                "| Entry | Type | Status | Risk |",
                "| --- | --- | --- | --- |",
            ]
        )
        for entry in sorted(grouped, key=lambda item: item["name"].casefold()):
            link = profile_link(entry["registry_file"])
            lines.append(
                f"| [{markdown_table_cell(entry['name'])}]({link}) | "
                f"`{markdown_table_code_cell(entry['artifact_type'])}` | "
                f"`{markdown_table_code_cell(entry['status'])}` | "
                f"`{markdown_table_code_cell(entry['risk_level'])}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def entry_links(entries: list[dict[str, Any]]) -> str:
    links = [
        f"[{markdown_table_cell(entry['name'])}]({profile_link(entry['registry_file'])})"
        for entry in sorted(entries, key=lambda item: item["name"].casefold())
    ]
    return "<br>".join(links)


def render_lookup_index(
    title: str,
    description: str,
    column_name: str,
    groups: dict[str, list[dict[str, Any]]],
    humanize_keys: bool = False,
) -> str:
    lines = [
        f"# {title}",
        "",
        description,
        "",
        "[Back to the catalog home](../README.md)",
        "",
        f"| {column_name} | Reviews |",
        "| --- | --- |",
    ]
    for group in sorted(groups, key=str.casefold):
        display_group = group.replace("_", " ") if humanize_keys else group
        lines.append(
            f"| {markdown_table_cell(display_group)} | {entry_links(groups[group])} |"
        )
    return "\n".join(lines) + "\n"


def display_ai_target(target: str) -> str:
    """Return a stable heading without coupling schema evolution to a hard-coded map."""
    return AI_TARGET_DISPLAY_NAMES.get(target, target.replace("_", " ").title())


def render_indexes(registry: dict[str, Any]) -> dict[str, str]:
    entries = registry["skills"]
    profiles = {
        entry["id"]: load_yaml(ROOT / entry["registry_file"], []) for entry in entries
    }
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

    use_case_groups: dict[str, list[dict[str, Any]]] = {}
    source_owner_groups: dict[str, list[dict[str, Any]]] = {}
    language_groups: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        profile = profiles[entry["id"]]
        for use_case in profile["useful_for"]:
            use_case_groups.setdefault(use_case, []).append(entry)
        source_owner_groups.setdefault(profile["source_owner"], []).append(entry)
        for language in profile["content_languages"]:
            language_groups.setdefault(language, []).append(entry)

    rendered["use_case"] = render_lookup_index(
        "Catalog by use case",
        "Concrete use cases declared in reviewed profiles, using the profile vocabulary.",
        "Use case",
        use_case_groups,
        humanize_keys=True,
    )
    rendered["company"] = render_lookup_index(
        "Catalog by publisher or company",
        "Groups use the public source account or publisher; they do not assert legal ownership.",
        "Public source owner",
        source_owner_groups,
    )
    rendered["language"] = render_lookup_index(
        "Catalog by content language",
        "Language refers to reviewed documentation, not an inferred programming language.",
        "Content language",
        language_groups,
    )

    lines = [
        "# Catalog by AI environment",
        "",
        "Compatibility describes documented applicability; it does not authorize installation "
        "or execution.",
        "",
        "[Back to the catalog home](../README.md)",
        "",
        "| Entry | "
        + " | ".join(display_ai_target(target) for target in registry["ai_targets"])
        + " |",
        "| --- | " + " | ".join("---" for _ in registry["ai_targets"]) + " |",
    ]
    for entry in entries:
        profile = profiles[entry["id"]]
        compatibility = profile["compatibility"]
        values = " | ".join(
            f"`{markdown_table_code_cell(compatibility[target])}`"
            for target in registry["ai_targets"]
        )
        lines.append(
            f"| [{markdown_table_cell(entry['name'])}]"
            f"({profile_link(entry['registry_file'])}) | {values} |"
        )
    rendered["ai"] = "\n".join(lines) + "\n"

    recent_lines = [
        "# Recent catalog reviews",
        "",
        "Review dates describe each profile's evidence check, not the source's latest release.",
        "",
        "[Back to the catalog home](../README.md)",
        "",
        "| Reviewed | Entry | Status | Risk | Review state |",
        "| --- | --- | --- | --- | --- |",
    ]
    recent_entries = sorted(entries, key=lambda item: item["name"].casefold())
    recent_entries.sort(
        key=lambda item: str(profiles[item["id"]]["review"].get("reviewed_at") or ""),
        reverse=True,
    )
    for entry in recent_entries:
        review = profiles[entry["id"]]["review"]
        reviewed_at = review.get("reviewed_at") or "unknown"
        recent_lines.append(
            f"| `{markdown_table_code_cell(reviewed_at)}` | "
            f"[{markdown_table_cell(entry['name'])}]({profile_link(entry['registry_file'])}) | "
            f"`{markdown_table_code_cell(entry['status'])}` | "
            f"`{markdown_table_code_cell(entry['risk_level'])}` | "
            f"`{markdown_table_code_cell(review['review_status'])}` |"
        )
    rendered["recent"] = "\n".join(recent_lines) + "\n"
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
            "use_case": ROOT / "docs" / "catalog_by_use_case.md",
            "company": ROOT / "docs" / "catalog_by_company.md",
            "ai": ROOT / "docs" / "catalog_by_ai.md",
            "status": ROOT / "docs" / "catalog_by_status.md",
            "risk": ROOT / "docs" / "catalog_by_risk.md",
            "language": ROOT / "docs" / "catalog_by_language.md",
            "recent": ROOT / "docs" / "catalog_recent_reviews.md",
        }
    errors: list[str] = []
    try:
        check_all_yaml(errors, ROOT)
        check_issue_forms(errors, ROOT)
        check_svg_files(errors, ROOT)
        raw_registry = load_yaml(REGISTRY_PATH, errors)
        registry = normalize_registry_schema(raw_registry, errors)
        if registry is None:
            check_markdown_format(errors, ROOT)
            check_internal_links(errors, ROOT)
            check_secrets(errors, ROOT)
            return errors

        entries_by_path: dict[str, dict[str, Any]] = {}
        valid_profile_paths: set[str] = set()
        ids: list[str] = []
        sources: list[str] = []
        for path in entry_paths(ROOT):
            entry = load_yaml(path, errors)
            if isinstance(entry, dict):
                relative = str(path.relative_to(ROOT))
                entries_by_path[relative] = entry
                ids.append(str(entry.get("id")))
                sources.append(str(entry.get("source")))
                if check_entry(path, entry, registry, errors, ENTRY_DIRECTORIES[path.parent.name]):
                    valid_profile_paths.add(relative)

        template_path = ROOT / "skills" / "profile-template.yml"
        template = load_yaml(template_path, errors)
        if template is not None:
            check_entry(template_path, template, registry, errors, "candidate")

        example_path = ROOT / "docs" / "examples" / "candidate-profile.yml"
        example = load_yaml(example_path, errors)
        if example is not None:
            check_entry(example_path, example, registry, errors, "candidate")

        for field, values in (("id", ids), ("source", sources)):
            duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
            if duplicates:
                errors.append(f"profiles: duplicate {field}: {', '.join(duplicates)}")

        check_registry(registry, entries_by_path, valid_profile_paths, errors)
        check_readme_catalog_count(registry, errors, ROOT)
        if not errors:
            check_or_write_indexes(registry, errors, write_indexes)
        check_markdown_format(errors, ROOT)
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
        help="regenerate the eight Markdown catalog indexes before validation",
    )
    args = parser.parse_args()
    errors = validate(write_indexes=args.write_indexes)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(
        "Registry validation passed: YAML, schema, profiles, indexes, Markdown, links, "
        "and secret patterns."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
