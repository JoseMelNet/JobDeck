"""Tests for FastAPI endpoints."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    @patch("api.test_connection", return_value=True)
    def test_health_returns_ok_when_db_is_connected(self, _mock_test_connection):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("api.analyze_vacancy_use_case")
    @patch("api.create_vacancy_use_case")
    def test_create_vacancy_calls_use_cases(self, mock_create_use_case, mock_analyze_use_case):
        mock_create_use_case.execute.return_value = {
            "success": True,
            "message": "saved",
            "id": 10,
        }

        response = self.client.post(
            "/vacantes",
            json={
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "remote",
                "link": "https://example.com",
                "descripcion": "Desc",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        mock_create_use_case.execute.assert_called_once()
        mock_analyze_use_case.execute.assert_called_once_with(10)

    @patch("api.create_vacancy_use_case")
    def test_create_vacancy_returns_500_when_repository_result_fails(self, mock_create_use_case):
        mock_create_use_case.execute.return_value = {
            "success": False,
            "message": "db error",
            "id": None,
        }

        response = self.client.post(
            "/vacantes",
            json={
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "remote",
                "descripcion": "Desc",
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "db error")

    @patch("api._run_analysis_task")
    @patch("api.create_vacancy_use_case")
    def test_create_vacancy_async_returns_task_metadata(self, mock_create_use_case, _mock_run_analysis_task):
        mock_create_use_case.execute.return_value = {
            "success": True,
            "message": "saved",
            "id": 15,
        }

        response = self.client.post(
            "/vacantes/async",
            json={
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "hybrid",
                "link": "https://example.com",
                "descripcion": "Desc",
            },
        )

        self.assertEqual(response.status_code, 202)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["id"], 15)
        self.assertEqual(body["status"], "queued")
        self.assertTrue(body["task_id"])

    def test_get_analysis_task_returns_status_when_task_exists(self):
        api.analysis_tasks["task-test"] = {
            "task_id": "task-test",
            "vacancy_id": 21,
            "status": "running",
            "step": "analyzing",
            "message": "Analizando",
            "error": None,
            "created_at": "2026-04-06T10:00:00Z",
            "updated_at": "2026-04-06T10:01:00Z",
        }

        response = self.client.get("/vacantes/tasks/task-test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "running")
        self.assertEqual(response.json()["vacancy_id"], 21)

    def test_get_analysis_job_legacy_alias_returns_status_when_task_exists(self):
        api.analysis_tasks["task-legacy"] = {
            "task_id": "task-legacy",
            "vacancy_id": 34,
            "status": "queued",
            "step": "saved",
            "message": "En cola",
            "error": None,
            "created_at": "2026-04-06T10:00:00Z",
            "updated_at": "2026-04-06T10:01:00Z",
        }

        response = self.client.get("/vacantes/jobs/task-legacy")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task_id"], "task-legacy")
        self.assertEqual(response.json()["status"], "queued")

    @patch("api.analysis_repository")
    def test_get_vacancy_analysis_returns_saved_analysis(self, mock_analysis_repository):
        mock_analysis_repository.get_by_vacancy_id.return_value = {
            "score_total": 88,
            "afinidad_general": "Alta",
            "decision_aplicacion": "Aplicar",
            "skills_match": ["SQL", "Python"],
            "skills_gap": ["dbt"],
            "fortalezas_principales": ["Analitica"],
            "riesgos_principales": ["Ingles"],
            "resumen_analisis": "Buen encaje para el rol.",
        }

        response = self.client.get("/vacantes/15/analysis")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vacancy_id"], 15)
        self.assertEqual(response.json()["analysis"]["score_total"], 88)

    @patch("api.analysis_repository")
    @patch("api.vacancy_repository")
    def test_get_vacancy_by_link_returns_existing_vacancy_and_analysis(
        self,
        mock_vacancy_repository,
        mock_analysis_repository,
    ):
        mock_vacancy_repository.get_by_link.return_value = {
            "id": 22,
            "empresa": "ACME",
            "cargo": "Data Analyst",
            "modalidad": "Remoto",
            "link": "https://www.linkedin.com/jobs/view/4384356134",
            "descripcion": "Desc",
            "fecha_registro": "2026-04-06T10:00:00",
            "motivo_archivo": None,
        }
        mock_analysis_repository.get_by_vacancy_id.return_value = {
            "score_total": 91,
            "afinidad_general": "Alta",
            "decision_aplicacion": "Aplicar",
        }

        response = self.client.get(
            "/vacantes/by-link",
            params={"link": "https://www.linkedin.com/jobs/view/4384356134?tracking=abc"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["found"])
        self.assertEqual(response.json()["vacancy"]["id"], 22)
        self.assertEqual(response.json()["analysis"]["score_total"], 91)

    @patch("api.vacancy_repository")
    def test_get_vacancy_by_link_returns_found_false_when_missing(self, mock_vacancy_repository):
        mock_vacancy_repository.get_by_link.return_value = None

        response = self.client.get(
            "/vacantes/by-link",
            params={"link": "https://www.linkedin.com/jobs/view/4384356134"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["found"])
        self.assertIsNone(response.json()["vacancy"])
        self.assertIsNone(response.json()["analysis"])


if __name__ == "__main__":
    unittest.main()
