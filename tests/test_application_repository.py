"""Tests for ApplicationRepository."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.infrastructure.persistence.repositories.application_repository import ApplicationRepository


class ApplicationRepositoryTests(unittest.TestCase):
    def test_clean_trims_and_normalizes_empty_values(self):
        self.assertEqual(ApplicationRepository._clean(" x "), "x")
        self.assertIsNone(ApplicationRepository._clean(" "))
        self.assertIsNone(ApplicationRepository._clean(None))

    def test_create_rejects_invalid_status_before_db(self):
        repository = ApplicationRepository()

        result = repository.create(vacante_id=1, estado="Invalid", fecha_aplicacion="2026-01-01")

        self.assertFalse(result["success"])
        self.assertIsNone(result["id"])

    @patch("app.infrastructure.persistence.repositories.application_repository.get_connection")
    def test_create_rejects_duplicate_application(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.side_effect = [[1]]
        get_connection_mock.return_value = conn
        repository = ApplicationRepository()

        result = repository.create(vacante_id=1, estado="Applied", fecha_aplicacion="2026-01-01")

        self.assertFalse(result["success"])
        self.assertIn("existe", result["message"])

    @patch("app.infrastructure.persistence.repositories.application_repository.get_connection")
    def test_count_by_status_accumulates_total(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [("Applied", 2), ("Rejected", 1)]
        get_connection_mock.return_value = conn
        repository = ApplicationRepository()

        result = repository.count_by_status()

        self.assertEqual(result["Applied"], 2)
        self.assertEqual(result["Rejected"], 1)
        self.assertEqual(result["Total"], 3)


if __name__ == "__main__":
    unittest.main()
