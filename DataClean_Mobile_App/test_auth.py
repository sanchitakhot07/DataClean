import tempfile
import unittest
from pathlib import Path

from auth import authenticate_user, register_user


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "users.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registered_user_can_authenticate(self):
        self.assertTrue(register_user("Sample_User", "correct-horse-123", self.database_path))
        self.assertTrue(
            authenticate_user("sample_user", "correct-horse-123", self.database_path)
        )

    def test_duplicate_username_is_rejected_case_insensitively(self):
        self.assertTrue(register_user("Sample_User", "correct-horse-123", self.database_path))
        self.assertFalse(
            register_user("sample_user", "another-password", self.database_path)
        )

    def test_invalid_password_does_not_authenticate(self):
        register_user("sample_user", "correct-horse-123", self.database_path)
        self.assertFalse(authenticate_user("sample_user", "wrong-password", self.database_path))

    def test_registration_rejects_weak_password(self):
        with self.assertRaises(ValueError):
            register_user("sample_user", "short", self.database_path)


if __name__ == "__main__":
    unittest.main()
