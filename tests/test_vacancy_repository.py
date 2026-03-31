"""Tests for VacancyRepository."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository


class VacancyRepositoryTests(unittest.TestCase):
    def test_create_rejects_invalid_modality_before_hitting_db(self):
        repository = VacancyRepository()

        result = repository.create(
            empresa="ACME",
            cargo="Analyst",
            modalidad="Invalid",
            descripcion="Desc",
        )

        self.assertFalse(result["success"])
        self.assertIsNone(result["id"])

    def test_row_to_vacancy_maps_expected_fields(self):
        repository = VacancyRepository()

        row = (1, "ACME", "Analyst", "Remoto", "http://x", "Desc", "2026-01-01", "Descartada")
        result = repository._row_to_vacancy(row)

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["empresa"], "ACME")
        self.assertEqual(result["motivo_archivo"], "Descartada")

    @patch("app.infrastructure.persistence.repositories.vacancy_repository.get_connection")
    def test_create_commits_when_insert_succeeds(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = [5]
        get_connection_mock.return_value = conn
        repository = VacancyRepository()

        result = repository.create(
            empresa="ACME",
            cargo="Analyst",
            modalidad="Remoto",
            descripcion="Desc",
            link=" https://example.com ",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["id"], 5)
        conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
