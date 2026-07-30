from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidatorUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw_registry = yaml.safe_load(VALIDATOR.REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.raw_registry = raw_registry
        errors: list[str] = []
        cls.registry = VALIDATOR.normalize_registry_schema(raw_registry, errors)
        assert cls.registry is not None, errors
        cls.profile_path = VALIDATOR.ROOT / "skills" / "profile-template.yml"
        cls.profile = yaml.safe_load(cls.profile_path.read_text(encoding="utf-8"))

    def profile_with_capability(
        self, capability: str, value: str, risk_level: str
    ) -> dict[str, object]:
        profile = copy.deepcopy(self.profile)
        profile["risk_level"] = risk_level
        profile["data_access"] = {
            field: "no" for field in VALIDATOR.REQUIRED_DATA_ACCESS_FIELDS
        }
        profile["data_access"][capability] = value
        return profile

    def entry_errors(self, profile: dict[str, object]) -> list[str]:
        errors: list[str] = []
        VALIDATOR.check_entry(
            self.profile_path,
            profile,
            self.registry,
            errors,
            "candidate",
        )
        return errors

    def test_public_https_url_is_valid(self) -> None:
        self.assertTrue(VALIDATOR.is_valid_public_url("https://example.com/project"))

    def test_http_url_is_rejected(self) -> None:
        self.assertFalse(VALIDATOR.is_valid_public_url("http://example.com/project"))

    def test_url_with_embedded_credentials_is_rejected(self) -> None:
        credential_url = "https://user:password" + "@example.com/project"
        self.assertFalse(VALIDATOR.is_valid_public_url(credential_url))

    def test_private_source_url_is_rejected(self) -> None:
        private_url = "https://" + "192.168." + "1.10/project"
        self.assertFalse(VALIDATOR.is_valid_public_url(private_url))

    def test_github_anchor_normalization(self) -> None:
        self.assertEqual(VALIDATOR.github_anchor("Quick start (safe)"), "quick-start-safe")

    def test_secret_scanner_detects_local_user_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local_path = "/" + "Users/example/private/file"
            (root / "sample.md").write_text(f"Path: {local_path}\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_secrets(errors, root)
            self.assertTrue(any("local user path" in error for error in errors))

    def test_internal_link_checker_detects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_internal_links(errors, root)
            self.assertTrue(any("broken internal link" in error for error in errors))

    def test_medium_risk_accepts_declared_network_access(self) -> None:
        errors = self.entry_errors(self.profile_with_capability("network", "yes", "medium"))
        self.assertFalse(any("below minimum" in error for error in errors), errors)

    def test_low_risk_rejects_declared_file_access(self) -> None:
        errors = self.entry_errors(self.profile_with_capability("local_files", "likely", "low"))
        self.assertTrue(any("below minimum 'medium'" in error for error in errors), errors)

    def test_high_risk_accepts_declared_browser_control(self) -> None:
        errors = self.entry_errors(
            self.profile_with_capability("browser_control", "possible", "high")
        )
        self.assertFalse(any("below minimum" in error for error in errors), errors)

    def test_medium_risk_rejects_declared_shell_access(self) -> None:
        errors = self.entry_errors(
            self.profile_with_capability("shell_commands", "yes", "medium")
        )
        self.assertTrue(any("below minimum 'high'" in error for error in errors), errors)

    def test_credentials_require_high_risk(self) -> None:
        accepted = self.entry_errors(
            self.profile_with_capability("credentials", "possible", "high")
        )
        rejected = self.entry_errors(
            self.profile_with_capability("credentials", "possible", "medium")
        )
        self.assertFalse(any("below minimum" in error for error in accepted), accepted)
        self.assertTrue(any("below minimum 'high'" in error for error in rejected), rejected)

    def test_every_declared_capability_enforces_its_documented_floor(self) -> None:
        lower_risk = {"medium": "low", "high": "medium"}
        for minimum, capabilities in VALIDATOR.CAPABILITY_RISK_FLOORS.items():
            for capability in capabilities:
                with self.subTest(capability=capability, outcome="accepted"):
                    accepted_errors = self.entry_errors(
                        self.profile_with_capability(capability, "possible", minimum)
                    )
                    self.assertFalse(
                        any("below minimum" in error for error in accepted_errors),
                        accepted_errors,
                    )
                with self.subTest(capability=capability, outcome="rejected"):
                    rejected_errors = self.entry_errors(
                        self.profile_with_capability(
                            capability,
                            "possible",
                            lower_risk[minimum],
                        )
                    )
                    self.assertTrue(
                        any(f"below minimum '{minimum}'" in error for error in rejected_errors),
                        rejected_errors,
                    )

    def test_use_cases_must_be_non_empty_strings(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["useful_for"] = ["valid use case", 123]
        errors = self.entry_errors(profile)
        self.assertTrue(
            any("useful_for values must be non-empty strings" in error for error in errors),
            errors,
        )

    def test_registry_file_accepts_only_canonical_profile_paths(self) -> None:
        self.assertEqual(
            VALIDATOR.normalize_registry_file("skills/candidates/example.yml"),
            "skills/candidates/example.yml",
        )
        self.assertEqual(
            VALIDATOR.normalize_registry_file("skills/accepted/example.yaml"),
            "skills/accepted/example.yaml",
        )
        rejected = (
            "docs/example.yml",
            "skills/candidates/../accepted/example.yml",
            "/skills/candidates/example.yml",
            "skills/candidates/example.json",
            "skills/candidates/nested/example.yml",
            "skills\\candidates\\example.yml",
        )
        for value in rejected:
            with self.subTest(value=value):
                self.assertIsNone(VALIDATOR.normalize_registry_file(value))

    def test_registry_rejects_unadmitted_and_incomplete_profiles(self) -> None:
        item = copy.deepcopy(self.registry["skills"][0])
        item["registry_file"] = "docs/external.yml"
        registry = dict(self.registry)
        registry["skills"] = [item]
        errors: list[str] = []
        VALIDATOR.check_registry(registry, {}, set(), errors)
        self.assertTrue(any("not admitted profiles" in error for error in errors), errors)

        profile_path = self.registry["skills"][0]["registry_file"]
        registry["skills"][0]["registry_file"] = profile_path
        errors = []
        VALIDATOR.check_registry(registry, {profile_path: {}}, set(), errors)
        self.assertTrue(any("not a complete valid profile" in error for error in errors), errors)

    def test_registry_schema_reports_missing_misspelled_and_wrong_type_fields(self) -> None:
        cases = []
        missing = copy.deepcopy(self.raw_registry)
        missing.pop("allowed_statuses")
        cases.append((missing, "missing fields: allowed_statuses"))
        misspelled = copy.deepcopy(self.raw_registry)
        misspelled["allowed_status"] = misspelled.pop("allowed_statuses")
        cases.append((misspelled, "unknown fields: allowed_status"))
        wrong_type = copy.deepcopy(self.raw_registry)
        wrong_type["ai_targets"] = "openai_codex"
        cases.append((wrong_type, "ai_targets must be a list"))

        for registry, expected in cases:
            with self.subTest(expected=expected):
                errors: list[str] = []
                normalized = VALIDATOR.normalize_registry_schema(registry, errors)
                self.assertIsNone(normalized)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_secret_scanner_rejects_file_directory_and_dangling_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_file = root / "target.txt"
            target_file.write_text("safe\n", encoding="utf-8")
            target_directory = root / "target-directory"
            target_directory.mkdir()
            links = (
                (root / "file-link", target_file),
                (root / "directory-link", target_directory),
                (root / "dangling-link", root / "missing-target"),
                (root / ".venv", target_directory),
            )
            try:
                for link, target in links:
                    link.symlink_to(target, target_is_directory=target == target_directory)
            except OSError as exc:
                self.skipTest(f"symbolic links are unavailable: {exc}")

            errors: list[str] = []
            VALIDATOR.check_secrets(errors, root)
            symlink_errors = [error for error in errors if "symbolic links" in error]
            self.assertEqual(len(symlink_errors), 4, errors)

    def test_internal_link_checker_detects_missing_html_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").write_text(
                '<img src="missing.svg" alt="Missing asset">\n', encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.check_internal_links(errors, root)
            self.assertTrue(any("broken internal link" in error for error in errors))

    def test_markdown_checker_requires_h1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").write_text("## Starts too deep\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_markdown_format(errors, root)
            self.assertTrue(any("level-one heading" in error for error in errors))

    def test_markdown_checker_detects_heading_jump(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").write_text("# Title\n\n### Skipped level\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_markdown_format(errors, root)
            self.assertTrue(any("heading level jumps" in error for error in errors))

    def test_markdown_checker_ignores_h1_inside_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.md").write_text(
                "# Real title\n\n```markdown\n# Example title\n```\n", encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.check_markdown_format(errors, root)
            self.assertFalse(any("level-one heading" in error for error in errors), errors)

    def test_all_yaml_checker_detects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "invalid.yml").write_text("key: [unterminated\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_all_yaml(errors, root)
            self.assertTrue(any("invalid YAML" in error for error in errors))

    def test_issue_form_checker_detects_missing_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            forms = root / ".github" / "ISSUE_TEMPLATE"
            forms.mkdir(parents=True)
            (forms / "invalid.yml").write_text(
                "name: Invalid\ndescription: Missing body\ntitle: Invalid\n", encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.check_issue_forms(errors, root)
            self.assertTrue(any("issue form missing" in error for error in errors))

    def test_repository_has_six_schema_valid_issue_forms(self) -> None:
        forms = VALIDATOR.ROOT / ".github" / "ISSUE_TEMPLATE"
        form_names = {
            path.name for path in forms.glob("*.yml") if path.name != "config.yml"
        }
        self.assertEqual(
            form_names,
            {
                "bug_report.yml",
                "documentation.yml",
                "feature_request.yml",
                "new_skill_review.yml",
                "question.yml",
                "repository_suggestion.yml",
            },
        )
        errors: list[str] = []
        VALIDATOR.check_issue_forms(errors, VALIDATOR.ROOT)
        self.assertEqual(errors, [])

    def test_issue_form_checker_rejects_invalid_controls_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            forms = root / ".github" / "ISSUE_TEMPLATE"
            forms.mkdir(parents=True)
            (forms / "invalid.yml").write_text(
                """name: Invalid Form
description: Exercises malformed controls.
title: "[Invalid]: "
body:
  - type: dropdown
    id: invalid.id
    attributes:
      label: Choice
      options: []
    validations:
      required: "yes"
  - type: checkboxes
    id: checks
    attributes:
      label: Checks
      options:
        - missing: label
""",
                encoding="utf-8",
            )
            (forms / "config.yml").write_text(
                "blank_issues_enabled: \"no\"\ncontact_links: []\n", encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.check_issue_forms(errors, root)
            expected_fragments = (
                "id may use only",
                "requires non-empty string options",
                "validations.required must be a boolean",
                "requires a label",
                "blank_issues_enabled must be a boolean",
                "contact_links must be a non-empty list",
            )
            for fragment in expected_fragments:
                with self.subTest(fragment=fragment):
                    self.assertTrue(any(fragment in error for error in errors), errors)

    def test_ai_index_labels_allow_new_registry_targets(self) -> None:
        self.assertEqual(VALIDATOR.display_ai_target("openai_codex"), "OpenAI Codex")
        self.assertEqual(VALIDATOR.display_ai_target("future_assistant"), "Future Assistant")

    def test_index_renderer_produces_all_eight_coherent_views(self) -> None:
        rendered = VALIDATOR.render_indexes(self.registry)
        self.assertEqual(rendered.keys(), VALIDATOR.INDEX_PATHS.keys())
        for name, content in rendered.items():
            with self.subTest(index=name):
                self.assertIn("[Back to the catalog home](../README.md)", content)

    def test_svg_checker_detects_invalid_xml(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "invalid.svg").write_text("<svg><broken></svg>", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_svg_files(errors, root)
            self.assertTrue(any("invalid SVG/XML" in error for error in errors))

    def test_readme_catalog_count_detects_stale_badge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Catalog\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.check_readme_catalog_count({"skills": [{}, {}]}, errors, root)
            self.assertTrue(any("badge is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
