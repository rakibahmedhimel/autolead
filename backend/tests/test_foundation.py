import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@127.0.0.1:1/test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("API_KEY_ENCRYPTION_SECRET", "test-encryption-secret")

from backend.app.auth.security import create_token, hash_password, normalize_email, verify_password
from backend.app.routers.projects import normalize_project_name
from backend.app.services.api_key_service import decrypt_key, encrypt_key, masked_key
from backend.app.services.spreadsheet_service import parse_upload, safe_cell, validate_public_url


class FoundationTests(unittest.TestCase):
    def test_project_name_normalization(self):
        self.assertEqual(normalize_project_name(" India   Files "), "india files")
        self.assertEqual(normalize_project_name("india files"), "india files")

    def test_email_and_password_security(self):
        self.assertEqual(normalize_email(" USER@Example.COM "), "user@example.com")
        password_hash = hash_password("correct horse battery staple")
        self.assertNotIn("correct horse", password_hash)
        self.assertTrue(verify_password("correct horse battery staple", password_hash))

    def test_jwt_contains_stable_user_identifier(self):
        token = create_token(42)
        import jwt
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
        self.assertEqual(payload["sub"], "42")

    def test_api_key_is_encrypted_and_masked(self):
        raw = "test-provider-secret-value-abcd"
        encrypted = encrypt_key(raw)
        self.assertNotIn(raw, encrypted)
        self.assertEqual(decrypt_key(encrypted), raw)
        self.assertEqual(masked_key("abcd"), "fc-****abcd")

    def test_csv_import_preserves_existing_values(self):
        parsed = parse_upload("data.csv", b"Website,Email\nhttps://example.com,old@example.com\n")
        self.assertEqual(parsed[0][2][0]["Email"], "old@example.com")

    def test_formula_injection_is_sanitized(self):
        self.assertEqual(safe_cell("=HYPERLINK(\"bad\")"), "'=HYPERLINK(\"bad\")")

    @patch("backend.app.services.spreadsheet_service.socket.getaddrinfo")
    def test_ssrf_private_ip_is_rejected(self, lookup):
        lookup.return_value = [(None, None, None, None, ("127.0.0.1", 443))]
        with self.assertRaises(ValueError):
            validate_public_url("https://localhost")


if __name__ == "__main__":
    unittest.main()
