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
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies")

        self.assertEqual(response.status_code, 200)
        self.assertIn('<span class="context-value">25</span>', response.text)
        self.assertIn("Vacantes visibles", response.text)
        self.assertIn("Pagina 1 de 2", response.text)
        self.assertIn("Empresa 20", response.text)
        self.assertNotIn("Empresa 21", response.text)
        self.assertNotIn("Sin detalle", response.text)
        self.assertIn('id="vacancies-shell"', response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertIn("Empresa 1 - Cargo 1", response.text)
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
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
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
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
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
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "has_application": False,
            }
            for item_id in range(1, 26)
        ]

        response = self.client.get("/app/vacancies?selected=25&page=1&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Empresa 25", response.text)
        self.assertIn("Pagina 3 de 3", response.text)
        self.assertIn("Empresa 25 - Cargo 25", response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertNotIn('title="Cerrar"', response.text)

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_list_partial_renders_workspace_rows_without_inline_detail(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": item_id,
                "empresa": f"Empresa {item_id}",
                "cargo": f"Cargo {item_id}",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": f"Descripcion {item_id}",
                "link": None,
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "has_application": False,
            }
            for item_id in range(1, 4)
        ]

        response = self.client.get("/app/vacancies/list?selected=2&q=Empresa&view=Todas&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn('data-selected-row="true"', response.text)
        self.assertNotIn('data-inline-detail="true"', response.text)
        self.assertNotIn("Descripcion 2", response.text)
        self.assertIn(
            'hx-get="/app/vacancies?selected=2&q=Empresa&view=Todas&page=1&page_size=20"',
            response.text,
        )
        self.assertIn('hx-target="#vacancies-shell"', response.text)

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_detail_partial_preserves_query_view_and_pagination(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": 25,
                "empresa": "Empresa 25",
                "cargo": "Cargo 25",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 25",
                "link": None,
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "has_application": False,
            }
        ]

        response = self.client.get("/app/vacancies/25/detail?q=data&view=Todas&page=3&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Empresa 25 - Cargo 25", response.text)
        self.assertIn('name="q" value="data"', response.text)
        self.assertIn('name="view" value="Todas"', response.text)
        self.assertIn('name="page" value="3"', response.text)
        self.assertIn('name="page_size" value="10"', response.text)
        self.assertIn("Pasar a seguimiento", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_shell_partial_renders_workspace_with_detail_panel(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": 2,
                "empresa": "Empresa 2",
                "cargo": "Cargo 2",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 2",
                "link": "https://example.com/vacancy",
                "analisis": {
                    "score_total": 88,
                    "decision_aplicacion": "Aplicar",
                    "afinidad_general": "Alta",
                    "resumen_analisis": "Buen encaje general",
                    "fortalezas_principales": ["SQL", "Python"],
                    "skills_match": ["SQL", "Python"],
                    "skills_gap": ["ETL"],
                    "ajustes_cv_recomendados": ["Destacar analitica"],
                    "encaje_estrategico": "Alto",
                },
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "88",
                "score_meta": {"tone": "green", "label": "88", "value": 88},
                "affinity_meta": {"tone": "green", "label": "Alta", "raw": "Alta"},
                "decision_meta": {"tone": "green", "label": "Aplicar", "raw": "Aplicar"},
                "has_application": False,
            }
        ]

        response = self.client.get("/app/vacancies/shell?selected=2&q=Empresa&view=Todas&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="layout-two-columns workspace-shell inbox-workspace"', response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertIn("Resumen ejecutivo", response.text)
        self.assertIn("Buen encaje general", response.text)
        self.assertIn("Pasar a seguimiento", response.text)
        self.assertNotIn('data-inline-detail="true"', response.text)

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancies_index_hx_request_returns_workspace_shell_only(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": 7,
                "empresa": "Empresa 7",
                "cargo": "Cargo 7",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 7",
                "link": None,
                "analisis": None,
                "status_label": "Registrada",
                "status_meta": {"tone": "gray", "label": "Registrada"},
                "score_label": "Sin score",
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "has_application": False,
            }
        ]

        response = self.client.get(
            "/app/vacancies?selected=7",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="workspace-toolbar"', response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertNotIn("<!doctype html>", response.text.lower())

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
        self.assertEqual(result[0]["score_meta"]["tone"], "green")
        mock_analysis_repository.get_by_vacancy_ids.assert_called_once_with([1, 2])
        mock_application_repository.list_all.assert_called_once()

    @patch("app.interfaces.web.routes.vacancies.application_repository")
    @patch("app.interfaces.web.routes.vacancies.analysis_repository")
    @patch("app.interfaces.web.routes.vacancies.vacancy_repository")
    def test_build_vacancy_items_excludes_archived_items(
        self,
        mock_vacancy_repository,
        mock_analysis_repository,
        mock_application_repository,
    ):
        mock_vacancy_repository.list_all.return_value = [
            {"id": 1, "empresa": "A", "cargo": "Role A", "modalidad": "Remoto", "fecha_registro": date(2026, 4, 2), "motivo_archivo": None},
            {"id": 2, "empresa": "B", "cargo": "Role B", "modalidad": "Presencial", "fecha_registro": date(2026, 4, 1), "motivo_archivo": "Otro"},
        ]
        mock_analysis_repository.get_by_vacancy_ids.return_value = {}
        mock_application_repository.list_all.return_value = []

        result = vacancies_routes._build_vacancy_items()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["status_label"], "Sin analizar")

    @patch("app.interfaces.web.routes.vacancies._next_visible_vacancy_id", return_value=9)
    @patch("app.interfaces.web.routes.vacancies.vacancy_repository")
    def test_discard_vacancy_redirects_back_to_inbox_with_next_selected(
        self,
        mock_vacancy_repository,
        _mock_next_visible,
    ):
        mock_vacancy_repository.archive.return_value = {"success": True, "message": "ok"}

        response = self.client.post(
            "/app/vacancies/7/discard",
            data={"q": "data", "view": "Todas", "page": "2", "page_size": "10"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/app/vacancies?selected=9&flash=vacancy_discarded&q=data&page=2&page_size=10",
        )
        mock_vacancy_repository.archive.assert_called_once_with(7, "Otro")

    def test_score_meta_maps_thresholds_to_expected_tones(self):
        self.assertEqual(vacancies_routes._score_meta({"score_total": 88})["tone"], "green")
        self.assertEqual(vacancies_routes._score_meta({"score_total": 68})["tone"], "amber")
        self.assertEqual(vacancies_routes._score_meta({"score_total": 42})["tone"], "red")
        self.assertEqual(vacancies_routes._score_meta(None)["tone"], "gray")

    def test_affinity_and_decision_meta_map_to_expected_tones(self):
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Alta"})["tone"], "green")
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Media"})["tone"], "amber")
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Baja"})["tone"], "red")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "Aplicar"})["tone"], "green")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "Revisar mas a fondo"})["tone"], "amber")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "No aplicar"})["tone"], "red")
