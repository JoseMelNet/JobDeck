"""Tests for ProfileRepository."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import Mock, patch

from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository


class ProfileRepositoryTests(unittest.TestCase):
    def test_clean_trims_and_normalizes_empty_values(self):
        self.assertEqual(ProfileRepository._clean(" Ana "), "Ana")
        self.assertIsNone(ProfileRepository._clean(" "))
        self.assertIsNone(ProfileRepository._clean(None))

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_active_profile_maps_row(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = (
            1,
            "Ana",
            "Data Analyst",
            "Bogota",
            "Calle 1",
            "123",
            "ana@example.com",
            "linkedin",
            "github",
            "Senior",
            5,
            1000,
            2000,
            "USD",
            "Remoto,Hibrido",
            "2026-01-01",
            "2026-01-02",
        )
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_active_profile()

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["nombre"], "Ana")
        self.assertEqual(result["modalidades_aceptadas"], "Remoto,Hibrido")

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_save_profile_updates_existing_profile(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = [7]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.save_profile({"nombre": " Ana ", "titulo_profesional": " Analyst "})

        self.assertTrue(result["success"])
        self.assertEqual(result["id"], 7)
        conn.commit.assert_called_once()

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_save_profile_inserts_when_no_existing_profile(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.side_effect = [None, [9]]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.save_profile({"nombre": "Ana", "titulo_profesional": "Analyst"})

        self.assertTrue(result["success"])
        self.assertEqual(result["id"], 9)

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_skills_maps_rows(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [(1, "DB", "SQL", "Avanzado")]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_skills(1)

        self.assertEqual(result, [{"id": 1, "categoria": "DB", "skill": "SQL", "nivel": "Avanzado"}])

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_add_skill_commits(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.add_skill(1, " DB ", " SQL ", " Avanzado ")

        self.assertTrue(result["success"])
        conn.commit.assert_called_once()

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_experiences_maps_boolean_flag(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [
            (1, "Analyst", "ACME", "Bogota", date(2020, 1, 1), None, 1, "Tech", "Do things", "Saved time")
        ]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_experiences(1)

        self.assertEqual(result[0]["cargo"], "Analyst")
        self.assertTrue(result[0]["es_trabajo_actual"])

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_update_experience_returns_not_found_when_rowcount_zero(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        cursor.rowcount = 0
        conn.cursor.return_value = cursor
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.update_experience(3, {"cargo": "Analyst", "empresa": "ACME"})

        self.assertFalse(result["success"])
        self.assertIn("No se encontro", result["message"])

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_add_experience_handles_current_job_by_storing_no_end_date(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.add_experience(
            1,
            {
                "cargo": "Analyst",
                "empresa": "ACME",
                "fecha_inicio": date(2020, 1, 1),
                "fecha_fin": date(2021, 1, 1),
                "es_trabajo_actual": True,
            },
        )

        self.assertTrue(result["success"])
        args = cursor.execute.call_args.args[1]
        self.assertIsNone(args[5])
        self.assertEqual(args[6], 1)

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_projects_maps_rows(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [
            (1, "Dashboard", "ACME", "Bogota", date(2024, 1, 1), None, 1, "Python", "Desc", "Impacto", "http://repo")
        ]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_projects(1)

        self.assertEqual(result[0]["nombre"], "Dashboard")
        self.assertTrue(result[0]["es_proyecto_actual"])

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_update_project_handles_current_project_by_storing_no_end_date(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        cursor.rowcount = 1
        conn.cursor.return_value = cursor
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.update_project(
            5,
            {
                "nombre": "Dashboard",
                "empresa": "ACME",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": date(2024, 6, 1),
                "es_proyecto_actual": True,
                "stack": "Python",
                "funciones": "Desc",
                "logros": "Impacto",
                "url_repositorio": "http://repo",
            },
        )

        self.assertTrue(result["success"])
        args = cursor.execute.call_args.args[1]
        self.assertIsNone(args[4])
        self.assertEqual(args[5], 1)
        self.assertEqual(args[10], 5)
        conn.commit.assert_called_once()

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_add_education_commits(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.add_education(
            1,
            {"titulo": "Systems", "institucion": "UNI", "fecha_inicio": date(2020, 1, 1)},
        )

        self.assertTrue(result["success"])
        conn.commit.assert_called_once()

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_courses_maps_rows(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [
            (1, "Python", "Coursera", date(2024, 1, 1), date(2024, 2, 1), "Completado", "http://cert")
        ]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_courses(1)

        self.assertEqual(result[0]["titulo"], "Python")
        self.assertEqual(result[0]["url_certificado"], "http://cert")

    @patch("app.infrastructure.persistence.repositories.profile_repository.get_connection")
    def test_get_certifications_maps_rows(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [
            (1, "AWS", "Amazon", date(2024, 1, 1), None, "Vigente", "http://credly")
        ]
        get_connection_mock.return_value = conn
        repository = ProfileRepository()

        result = repository.get_certifications(1)

        self.assertEqual(result[0]["titulo"], "AWS")
        self.assertEqual(result[0]["status"], "Vigente")


if __name__ == "__main__":
    unittest.main()
