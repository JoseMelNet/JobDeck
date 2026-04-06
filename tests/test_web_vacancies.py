"""Tests for the web vacancies routes."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
from app.interfaces.web.routes import vacancies as vacancies_routes


class WebVacanciesTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.vacancies.analyze_vacancy_use_case")
    @patch("app.interfaces.web.routes.vacancies.create_vacancy_use_case")
    def test_create_vacancy_accepts_unaccented_hybrid_modality(
        self,
        mock_create_use_case,
        mock_analyze_use_case,
        _mock_nav,
        _mock_metrics,
    ):
        mock_create_use_case.execute.return_value = {"success": True, "id": 10}
        mock_analyze_use_case.execute.return_value = {"omitido": False}

        response = self.client.post(
            "/app/vacancies/new",
            data={
                "empresa": "ACME",
                "cargo": "Data Analyst",
                "modalidad": "Hibrido",
                "descripcion": "Desc",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/app/vacancies?selected=10&flash=vacancy_created")
        mock_create_use_case.execute.assert_called_once_with(
            empresa="ACME",
            cargo="Data Analyst",
            modalidad="Hibrido",
            descripcion="Desc",
            link=None,
        )
        mock_analyze_use_case.execute.assert_called_once_with(10)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_inbox_shows_more_than_twenty_vacancies(self, mock_build_items, _mock_nav, _mock_metrics):
        mock_build_items.return_value = [
            {
                "id": item_id,
                "empresa": f"Empresa {item_id}",
                "cargo": f"Cargo {item_id}",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies")

        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="summary-value">25</div>', response.text)
        self.assertIn("Pagina 1 de 2", response.text)
        self.assertIn("Empresa 20", response.text)
        self.assertNotIn("Empresa 21", response.text)
        mock_build_items.assert_called_once_with(limit=None)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_inbox_paginates_results(self, mock_build_items, _mock_nav, _mock_metrics):
        mock_build_items.return_value = [
            {
                "id": item_id,
                "empresa": f"Empresa {item_id}",
                "cargo": f"Cargo {item_id}",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Empresa 21", response.text)
        self.assertIn("Empresa 25", response.text)
        self.assertNotIn("Empresa 20", response.text)
        self.assertIn("Pagina 2 de 2", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_inbox_supports_custom_page_size(self, mock_build_items, _mock_nav, _mock_metrics):
        mock_build_items.return_value = [
            {
                "id": item_id,
                "empresa": f"Empresa {item_id}",
                "cargo": f"Cargo {item_id}",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies?page_size=10&page=3")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Empresa 21", response.text)
        self.assertIn("Empresa 25", response.text)
        self.assertNotIn("Empresa 20", response.text)
        self.assertIn("Pagina 3 de 3", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_inbox_moves_to_page_of_selected_vacancy(self, mock_build_items, _mock_nav, _mock_metrics):
        mock_build_items.return_value = [
            {
                "id": item_id,
                "empresa": f"Empresa {item_id}",
                "cargo": f"Cargo {item_id}",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies?selected=25&page=1&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Empresa 25", response.text)
        self.assertIn("Pagina 3 de 3", response.text)
        self.assertIn("Empresa 25 - Cargo 25", response.text)

    @patch("app.interfaces.web.routes.vacancies.application_repository")
    @patch("app.interfaces.web.routes.vacancies.analysis_repository")
    @patch("app.interfaces.web.routes.vacancies.vacancy_repository")
    def test_build_vacancy_items_batches_analysis_and_tracking_queries(
        self,
        mock_vacancy_repository,
        mock_analysis_repository,
        mock_application_repository,
    ):
        mock_vacancy_repository.list_all.return_value = [
            {"id": 1, "empresa": "A", "cargo": "Role A", "modalidad": "Remoto", "fecha_registro": date(2026, 4, 2)},
            {"id": 2, "empresa": "B", "cargo": "Role B", "modalidad": "Presencial", "fecha_registro": date(2026, 4, 1)},
        ]
        mock_analysis_repository.get_by_vacancy_ids.return_value = {
            1: {"score_total": 87},
        }
        mock_application_repository.list_all.return_value = [{"vacante_id": 2}]

        result = vacancies_routes._build_vacancy_items()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["status_label"], "Analizada")
        self.assertEqual(result[1]["status_label"], "En seguimiento")
        mock_analysis_repository.get_by_vacancy_ids.assert_called_once_with([1, 2])
        mock_application_repository.list_all.assert_called_once()
