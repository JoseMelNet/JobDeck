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

    @patch("api._run_analysis_job")
    @patch("api.create_vacancy_use_case")
    def test_create_vacancy_async_returns_job_metadata(self, mock_create_use_case, _mock_run_analysis_job):
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
        self.assertTrue(body["job_id"])

    def test_get_analysis_job_returns_status_when_job_exists(self):
        api.analysis_jobs["job-test"] = {
            "job_id": "job-test",
            "vacancy_id": 21,
            "status": "running",
            "step": "analyzing",
            "message": "Analizando",
            "error": None,
            "created_at": "2026-04-06T10:00:00Z",
            "updated_at": "2026-04-06T10:01:00Z",
        }

        response = self.client.get("/vacantes/jobs/job-test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "running")
        self.assertEqual(response.json()["vacancy_id"], 21)

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


if __name__ == "__main__":
    unittest.main()
