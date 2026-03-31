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


if __name__ == "__main__":
    unittest.main()
