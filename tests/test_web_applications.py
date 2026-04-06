"""Tests for the web applications routes."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class WebApplicationsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_renders_tracking_page(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.list_all.return_value = [
            {
                "id": 7,
                "vacante_id": 3,
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "Remoto",
                "link": "https://example.com",
                "fecha_aplicacion": date(2026, 4, 1),
                "estado": "Pending",
                "nombre_recruiter": None,
                "email_recruiter": None,
                "telefono_recruiter": None,
                "notas": "Pendiente",
                "fecha_registro": date(2026, 4, 1),
            }
        ]

        response = self.client.get("/app/applications")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Seguimiento", response.text)
        self.assertIn("ACME", response.text)
        self.assertIn("Pendiente por aplicar", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_update_status_hx_returns_shell_with_flash(self, mock_repository):
        mock_repository.update_status.return_value = {"success": True}
        mock_repository.list_all.return_value = [
            {
                "id": 7,
                "vacante_id": 3,
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "Remoto",
                "link": "https://example.com",
                "fecha_aplicacion": date(2026, 4, 1),
                "estado": "Applied",
                "nombre_recruiter": None,
                "email_recruiter": None,
                "telefono_recruiter": None,
                "notas": "Aplicada",
                "fecha_registro": date(2026, 4, 1),
            }
        ]

        response = self.client.post(
            "/app/applications/7/status",
            data={"target_state": "Applied", "q": "", "state": "Todos"},
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("El estado de la aplicacion fue actualizado.", response.text)
        mock_repository.update_status.assert_called_once_with(7, "Applied")

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_paginates_results(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.list_all.return_value = [
            {
                "id": item_id,
                "vacante_id": item_id,
                "empresa": f"ACME {item_id}",
                "cargo": f"Role {item_id}",
                "modalidad": "Remoto",
                "link": "https://example.com",
                "fecha_aplicacion": date(2026, 4, 1),
                "estado": "Pending",
                "nombre_recruiter": None,
                "email_recruiter": None,
                "telefono_recruiter": None,
                "notas": "",
                "fecha_registro": date(2026, 4, 1),
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/applications?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACME 21", response.text)
        self.assertIn("ACME 25", response.text)
        self.assertNotIn("ACME 20", response.text)
        self.assertIn("Pagina 2 de 2", response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_supports_custom_page_size(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.list_all.return_value = [
            {
                "id": item_id,
                "vacante_id": item_id,
                "empresa": f"ACME {item_id}",
                "cargo": f"Role {item_id}",
                "modalidad": "Remoto",
                "link": "https://example.com",
                "fecha_aplicacion": date(2026, 4, 1),
                "estado": "Pending",
                "nombre_recruiter": None,
                "email_recruiter": None,
                "telefono_recruiter": None,
                "notas": "",
                "fecha_registro": date(2026, 4, 1),
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/applications?page_size=10&page=3")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACME 21", response.text)
        self.assertIn("ACME 25", response.text)
        self.assertNotIn("ACME 20", response.text)
        self.assertIn("Pagina 3 de 3", response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_moves_to_page_of_selected_application(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.list_all.return_value = [
            {
                "id": item_id,
                "vacante_id": item_id,
                "empresa": f"ACME {item_id}",
                "cargo": f"Role {item_id}",
                "modalidad": "Remoto",
                "link": "https://example.com",
                "fecha_aplicacion": date(2026, 4, 1),
                "estado": "Pending",
                "nombre_recruiter": None,
                "email_recruiter": None,
                "telefono_recruiter": None,
                "notas": "",
                "fecha_registro": date(2026, 4, 1),
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/applications?selected=25&page=1&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACME 25", response.text)
        self.assertIn("Pagina 3 de 3", response.text)
        self.assertIn("ACME 25 - Role 25", response.text)
