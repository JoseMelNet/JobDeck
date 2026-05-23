"""Tests for database configuration helpers."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.infrastructure.persistence import connection


class ConnectionConfigTests(unittest.TestCase):
    def test_build_connection_string_raises_clear_error_when_credentials_are_missing(self):
        fake_settings = SimpleNamespace(
            db_server="localhost\\MSSQLSERVER2025",
            db_database="job_postings_mvp",
            db_user=None,
            db_password=None,
        )

        with patch.object(connection, "settings", fake_settings):
            with self.assertRaises(connection.DatabaseConfigurationError) as ctx:
                connection.build_connection_string()

        self.assertIn("DB_USER", str(ctx.exception))
        self.assertIn("DB_PASSWORD", str(ctx.exception))

    def test_test_connection_returns_false_when_credentials_are_missing(self):
        fake_settings = SimpleNamespace(
            db_server="localhost\\MSSQLSERVER2025",
            db_database="job_postings_mvp",
            db_user=None,
            db_password=None,
        )

        with patch.object(connection, "settings", fake_settings):
            self.assertFalse(connection.test_connection())

    def test_build_safe_connection_summary_redacts_credentials(self):
        fake_settings = SimpleNamespace(
            db_server="localhost\\MSSQLSERVER2025",
            db_database="job_postings_mvp",
            db_user="sa",
            db_password="super-secret-password",
        )

        with patch.object(connection, "settings", fake_settings):
            with patch.object(connection, "get_odbc_driver", return_value="ODBC Driver 17 for SQL Server"):
                summary = connection.build_safe_connection_summary()

        self.assertIn("UID=<configured>", summary)
        self.assertIn("PWD=<configured>", summary)
        self.assertNotIn("sa", summary)
        self.assertNotIn("super-secret-password", summary)


if __name__ == "__main__":
    unittest.main()
