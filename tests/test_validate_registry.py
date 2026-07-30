from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_registry", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidatorUnitTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
