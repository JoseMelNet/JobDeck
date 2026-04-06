"""Tests for the web profile routes."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class WebProfileTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_index_renders_profile_shell(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = [{"id": 1, "categoria": "Data", "skill": "SQL", "nivel": "Avanzado"}]
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Mi Perfil", response.text)
        self.assertIn("Jose", response.text)
        self.assertIn("SQL", response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_save_profile_hx_returns_profile_shell(self, mock_repository):
        mock_repository.save_profile.return_value = {"success": True, "id": 1}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
            "nivel_actual": "Mid",
            "anos_experiencia": 3,
            "moneda": "COP",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/save",
            data={
                "nombre": "Jose",
                "titulo_profesional": "Data Analyst",
                "nivel_actual": "Mid",
                "anos_experiencia": "3",
                "moneda": "COP",
                "modalidades_aceptadas": ["Remoto", "Hibrido"],
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Los datos principales del perfil fueron guardados.", response.text)
        payload = mock_repository.save_profile.call_args.args[0]
        self.assertEqual(payload["modalidades_aceptadas"], "Remoto,Hibrido")
