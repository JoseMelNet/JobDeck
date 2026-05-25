"""Tests for the web vacancies routes."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
from app.interfaces.web.routes import vacancies as vacancies_routes


def _mock_decision_signal(analysis: dict | None) -> dict:
    return vacancies_routes._build_decision_signal(analysis)


class WebVacanciesTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    def test_vacancy_description_css_uses_details_instead_of_target_reveal(self):
        css = Path("app/interfaces/web/static/css/app.css").read_text(encoding="utf-8")

        self.assertNotIn(".vacancy-description-reader:target", css)
        self.assertIn(".vacancy-description-reader[open] .vacancy-description-summary::after", css)

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
                "decision_signal": _mock_decision_signal(None),
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
                "decision_signal": _mock_decision_signal(None),
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
                "decision_signal": _mock_decision_signal(None),
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
                "decision_signal": _mock_decision_signal(None),
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
                "id": 1,
                "empresa": "Empresa 1",
                "cargo": "Cargo 1",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 1",
                "link": None,
                "analisis": {"score_total": 43, "decision_aplicacion": "Descartar"},
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "43",
                "score_meta": {"tone": "red", "label": "43", "value": 43},
                "affinity_meta": {"tone": "red", "label": "Baja", "raw": "Baja"},
                "decision_meta": {"tone": "red", "label": "Descartar", "raw": "Descartar"},
                "decision_signal": _mock_decision_signal({"score_total": 43, "decision_aplicacion": "Descartar"}),
                "decision_visual_tone": "red",
                "decision_compact_label": "Descartar",
                "has_application": False,
            },
            {
                "id": 2,
                "empresa": "Empresa 2",
                "cargo": "Cargo 2",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 2",
                "link": None,
                "analisis": {"score_total": 64, "decision_aplicacion": "Aplicar si sobra tiempo"},
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "64",
                "score_meta": {"tone": "amber", "label": "64", "value": 64},
                "affinity_meta": {"tone": "amber", "label": "Media", "raw": "Media"},
                "decision_meta": {"tone": "green", "label": "Aplicar si sobra tiempo", "raw": "Aplicar si sobra tiempo"},
                "decision_signal": _mock_decision_signal(
                    {"score_total": 64, "decision_aplicacion": "Aplicar si sobra tiempo"}
                ),
                "decision_visual_tone": "amber",
                "decision_compact_label": "Si hay tiempo",
                "has_application": False,
            },
            {
                "id": 3,
                "empresa": "Empresa 3",
                "cargo": "Cargo 3",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 3",
                "link": None,
                "analisis": None,
                "status_label": "Sin analizar",
                "status_meta": {"tone": "gray", "label": "Sin analizar"},
                "score_label": "Sin score",
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_signal": _mock_decision_signal(None),
                "decision_visual_tone": "gray",
                "decision_compact_label": "Pendiente de analisis",
                "has_application": False,
            },
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
        self.assertIn('class="opportunity-recommendation tone-amber"', response.text)
        self.assertIn("Si hay tiempo", response.text)
        self.assertIn('title="Score 64">64</span>', response.text)
        self.assertIn('title="Aplicar si sobra tiempo · Score 64"', response.text)
        self.assertIn('title="Score 64"', response.text)
        self.assertNotIn('opportunity-recommendation-score" title="Descartar"', response.text)

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
                "decision_signal": _mock_decision_signal(None),
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
        self.assertIn("Descripcion completa", response.text)
        self.assertIn("Texto original de la vacante", response.text)
        self.assertIn("Descripcion 25", response.text)
        self.assertIn('<details class="description-disclosure vacancy-description vacancy-description-reader">', response.text)
        self.assertIn('<summary class="vacancy-description-summary">', response.text)
        self.assertIn('class="vacancy-description-body vacancy-description-content"', response.text)
        self.assertNotIn("#vacancy-description-25", response.text)
        self.assertNotIn('href="/app/vacancies?selected=25', response.text)
        self.assertNotIn("modal", response.text.lower())
        self.assertNotIn("overlay", response.text.lower())

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_detail_partial_uses_view_tracking_cta_for_existing_application(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": 25,
                "empresa": "Empresa 25",
                "cargo": "Cargo 25",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 25",
                "link": "https://example.com/vacancy/25",
                "analisis": None,
                "status_label": "En seguimiento",
                "status_meta": {"tone": "blue", "label": "En seguimiento"},
                "score_label": "Sin score",
                "score_meta": {"tone": "gray", "label": "Sin analisis", "value": None},
                "affinity_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_meta": {"tone": "gray", "label": "-", "raw": None},
                "decision_signal": _mock_decision_signal(None),
                "has_application": True,
                "tracking_application_id": 77,
            }
        ]

        response = self.client.get("/app/vacancies/25/detail?q=data&view=Todas&page=3&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ver seguimiento", response.text)
        self.assertIn('href="/app/applications?selected=77"', response.text)
        self.assertNotIn("Ir a seguimiento", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_detail_partial_hides_null_metadata_values(self, mock_build_items):
        mock_build_items.return_value = [
            {
                "id": 31,
                "empresa": "Empresa 31",
                "cargo": "Cargo 31",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 31",
                "link": None,
                "analisis": {
                    "seniority_inferido": "null",
                    "salario_detectado": "",
                    "aspiracion_salarial_sugerida": None,
                },
                "detail_meta_items": ["01/04/2026", "Remoto"],
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "70",
                "score_meta": {"tone": "amber", "label": "70", "value": 70},
                "affinity_meta": {"tone": "amber", "label": "Media", "raw": "Media"},
                "decision_meta": {"tone": "amber", "label": "Revisar", "raw": "Revisar"},
                "decision_signal": _mock_decision_signal(
                    {"score_total": 70, "decision_aplicacion": "Revisar"}
                ),
                "decision_visual_tone": "amber",
                "decision_compact_label": "Revisar",
                "has_application": False,
            }
        ]

        response = self.client.get("/app/vacancies/31/detail")

        self.assertEqual(response.status_code, 200)
        self.assertIn("01/04/2026", response.text)
        self.assertIn("Remoto", response.text)
        self.assertNotIn(">null<", response.text)
        self.assertNotIn(">None<", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[{"label": "Aplicaciones", "value": 9}, {"label": "Rechazadas", "value": 2}])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_shell_partial_renders_workspace_with_detail_panel(self, mock_build_items, _mock_metrics):
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
                "detail_meta_items": ["01/04/2026", "Remoto"],
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "88",
                "score_meta": {"tone": "green", "label": "88", "value": 88},
                "affinity_meta": {"tone": "green", "label": "Alta", "raw": "Alta"},
                "decision_meta": {"tone": "green", "label": "Aplicar", "raw": "Aplicar"},
                "decision_signal": _mock_decision_signal({"score_total": 88, "decision_aplicacion": "Aplicar"}),
                "decision_visual_tone": "green",
                "decision_compact_label": "Si",
                "has_application": False,
            }
        ]

        response = self.client.get("/app/vacancies/shell?selected=2&q=Empresa&view=Todas&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="vacancies-shell"', response.text)
        self.assertIn('class="layout-two-columns workspace-shell inbox-workspace"', response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertIn("Vacantes visibles", response.text)
        self.assertIn("Aplicaciones", response.text)
        self.assertIn("Resumen ejecutivo", response.text)
        self.assertIn("Buen encaje general", response.text)
        self.assertIn("Pasar a seguimiento", response.text)
        self.assertNotIn('data-inline-detail="true"', response.text)
        self.assertIn("Descripcion completa", response.text)
        self.assertIn("Texto original de la vacante", response.text)
        self.assertIn('<details class="description-disclosure vacancy-description vacancy-description-reader">', response.text)
        self.assertIn('<summary class="vacancy-description-summary">', response.text)
        self.assertNotIn("#vacancy-description-2", response.text)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[{"label": "Aplicaciones", "value": 9}, {"label": "Rechazadas", "value": 2}])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancy_detail_panel_uses_decision_tone_instead_of_score_tone(self, mock_build_items, _mock_metrics):
        analysis = {
            "score_total": 88,
            "decision_aplicacion": "Aplicar si sobra tiempo",
            "afinidad_general": "Alta",
            "resumen_analisis": "Buen encaje, pero no prioritario",
        }
        mock_build_items.return_value = [
            {
                "id": 8,
                "empresa": "Empresa 8",
                "cargo": "Cargo 8",
                "modalidad": "Remoto",
                "fecha_registro": date(2026, 4, 1),
                "descripcion": "Descripcion 8",
                "link": None,
                "analisis": analysis,
                "detail_meta_items": ["01/04/2026", "Remoto"],
                "status_label": "Analizada",
                "status_meta": {"tone": "green", "label": "Analizada"},
                "score_label": "88",
                "score_meta": {"tone": "green", "label": "88", "value": 88},
                "affinity_meta": {"tone": "green", "label": "Alta", "raw": "Alta"},
                "decision_meta": {"tone": "amber", "label": "Aplicar si sobra tiempo", "raw": "Aplicar si sobra tiempo"},
                "decision_signal": _mock_decision_signal(analysis),
                "decision_visual_tone": "amber",
                "decision_compact_label": "Si hay tiempo",
                "has_application": False,
            }
        ]

        response = self.client.get("/app/vacancies/shell?selected=8")

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="decision-headline tone-amber"', response.text)
        self.assertIn("Aplicar si sobra tiempo", response.text)
        self.assertIn('class="analysis-pill opportunity-score-pill tone-green"', response.text)

    @patch("app.interfaces.web.routes.vacancies._build_metrics", return_value=[{"label": "Aplicaciones", "value": 9}, {"label": "Rechazadas", "value": 2}])
    @patch("app.interfaces.web.routes.vacancies._build_vacancy_items")
    def test_vacancies_index_hx_request_returns_workspace_shell_only(self, mock_build_items, _mock_metrics):
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
                "decision_signal": _mock_decision_signal(None),
                "decision_visual_tone": "gray",
                "decision_compact_label": "Pendiente de analisis",
                "has_application": False,
            }
        ]

        response = self.client.get(
            "/app/vacancies?selected=7",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="vacancies-shell"', response.text)
        self.assertIn('class="workspace-toolbar"', response.text)
        self.assertIn("Vacantes visibles", response.text)
        self.assertIn("Aplicaciones", response.text)
        self.assertIn('id="vacancy-detail"', response.text)
        self.assertNotIn("<!doctype html>", response.text.lower())
        self.assertIn("Filtrar", response.text)
        self.assertNotIn(">Aplicar</button>", response.text)

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
        mock_application_repository.list_all.return_value = [{"id": 12, "vacante_id": 2}]

        result = vacancies_routes._build_vacancy_items()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["status_label"], "Analizada")
        self.assertEqual(result[1]["status_label"], "En seguimiento")
        self.assertEqual(result[1]["tracking_application_id"], 12)
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
        self.assertEqual(vacancies_routes._score_meta(None)["band"], "unknown")

    def test_affinity_and_decision_meta_map_to_expected_tones(self):
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Alta"})["tone"], "green")
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Media"})["tone"], "amber")
        self.assertEqual(vacancies_routes._affinity_meta({"afinidad_general": "Baja"})["tone"], "red")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "Aplicar"})["tone"], "green")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "Revisar mas a fondo"})["tone"], "amber")
        self.assertEqual(vacancies_routes._decision_meta({"decision_aplicacion": "No aplicar"})["tone"], "red")

    def test_decision_signal_maps_apply_strong_to_green(self):
        signal = vacancies_routes._build_decision_signal(
            {"score_total": 93, "decision_aplicacion": "Aplicar sí o sí"}
        )

        self.assertEqual(signal["decision_normalized"], "apply_strong")
        self.assertEqual(signal["decision_compact_label"], "Si")
        self.assertEqual(signal["display_tone"], "green")
        self.assertEqual(signal["score_tone"], "green")

    def test_decision_signal_keeps_apply_later_amber_even_with_high_score(self):
        signal = vacancies_routes._build_decision_signal(
            {"score_total": 85, "decision_aplicacion": "Aplicar si sobra tiempo"}
        )

        self.assertEqual(signal["decision_compact_label"], "Si hay tiempo")
        self.assertEqual(signal["decision_tone"], "amber")
        self.assertEqual(signal["display_tone"], "amber")
        self.assertEqual(signal["score_tone"], "green")
        self.assertEqual(signal["coherence_status"], "cautious_high_score")

    def test_decision_signal_keeps_discard_red_even_with_medium_score(self):
        signal = vacancies_routes._build_decision_signal(
            {"score_total": 64, "decision_aplicacion": "Descartar"}
        )

        self.assertEqual(signal["decision_compact_label"], "No")
        self.assertEqual(signal["display_tone"], "red")
        self.assertEqual(signal["score_tone"], "amber")
        self.assertEqual(signal["coherence_status"], "cautious_discard")

    def test_decision_signal_handles_missing_score_with_existing_decision(self):
        signal = vacancies_routes._build_decision_signal(
            {"decision_aplicacion": "Aplicar sí o sí"}
        )

        self.assertEqual(signal["display_tone"], "green")
        self.assertEqual(signal["score_band"], "unknown")
        self.assertEqual(signal["coherence_status"], "missing_score")

    def test_decision_signal_handles_unknown_decision_with_existing_score(self):
        signal = vacancies_routes._build_decision_signal(
            {"score_total": 77, "decision_aplicacion": "Tal vez luego"}
        )

        self.assertEqual(signal["decision_normalized"], "unknown")
        self.assertEqual(signal["display_tone"], "gray")
        self.assertEqual(signal["score_tone"], "amber")
        self.assertEqual(signal["coherence_status"], "unknown_decision")
        self.assertEqual(signal["decision_compact_label"], "Sin decision")

    def test_compact_decision_label_uses_normalized_contract(self):
        self.assertEqual(
            vacancies_routes._compact_decision_label({"decision_aplicacion": "Aplicar si sobra tiempo"}),
            "Si hay tiempo",
        )
        self.assertEqual(
            vacancies_routes._compact_decision_label({"decision_aplicacion": "Aplicar sí o sí"}),
            "Si",
        )
        self.assertEqual(
            vacancies_routes._compact_decision_label({"decision_aplicacion": "Descartar"}),
            "No",
        )

    def test_clean_display_value_filters_garbage(self):
        self.assertIsNone(vacancies_routes._clean_display_value(None))
        self.assertIsNone(vacancies_routes._clean_display_value("null"))
        self.assertIsNone(vacancies_routes._clean_display_value(" "))
        self.assertEqual(vacancies_routes._clean_display_value("Remoto"), "Remoto")
