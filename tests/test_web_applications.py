"""Tests for the web applications routes."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

import api
from app.interfaces.web.presentation.application_signals import (
    build_follow_up_signals,
    pick_compact_follow_up_signal,
)


def _analysis_item(
    *,
    score_total=88,
    decision_aplicacion="Aplicar si sobra tiempo",
    justificacion_decision: str | None = None,
    resumen_analisis: str | None = None,
    fortalezas_principales: list[str] | None = None,
    riesgos_principales: list[str] | None = None,
) -> dict:
    analysis = {
        "score_total": score_total,
        "decision_aplicacion": decision_aplicacion,
        "justificacion_decision": justificacion_decision,
        "resumen_analisis": resumen_analisis,
        "fortalezas_principales": fortalezas_principales or [],
        "riesgos_principales": riesgos_principales or [],
    }
    return analysis


def _application_item(
    item_id: int,
    *,
    status: str = "Pending",
    company: str | None = None,
    role: str | None = None,
    notes: str = "",
    recruiter: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    application_date: date | None = None,
    registered_date: date | None = None,
) -> dict:
    return {
        "id": item_id,
        "vacante_id": item_id,
        "empresa": company or f"ACME {item_id}",
        "cargo": role or f"Role {item_id}",
        "modalidad": "Remoto",
        "link": "https://example.com",
        "fecha_aplicacion": application_date or date(2026, 4, 1),
        "estado": status,
        "nombre_recruiter": recruiter,
        "email_recruiter": email,
        "telefono_recruiter": phone,
        "notas": notes,
        "fecha_registro": registered_date or date(2026, 4, 1),
    }


class WebApplicationsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)
        self.analysis_repository_patcher = patch("app.interfaces.web.routes.applications.analysis_repository")
        self.mock_analysis_repository = self.analysis_repository_patcher.start()
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {}
        self.addCleanup(self.analysis_repository_patcher.stop)

    def test_pending_signal_includes_pending_por_aplicar_copy(self):
        signals = build_follow_up_signals(
            _application_item(1, status="Pending", application_date=date(2026, 5, 24)),
            today=date(2026, 5, 25),
        )

        self.assertEqual(signals[0]["label"], "Pendiente por aplicar")
        self.assertNotIn("Aplicada hace", " ".join(signal["label"] for signal in signals))

    def test_old_pending_signal_prioritizes_lleva_tiempo_pendiente(self):
        signals = build_follow_up_signals(
            _application_item(1, status="Pending", application_date=date(2026, 5, 10)),
            today=date(2026, 5, 25),
        )

        self.assertEqual(signals[0]["label"], "Lleva tiempo pendiente")
        self.assertEqual(pick_compact_follow_up_signal(signals)["label"], "Lleva tiempo pendiente")

    def test_old_applied_signal_uses_applied_threshold(self):
        signals = build_follow_up_signals(
            _application_item(1, status="Applied", application_date=date(2026, 5, 1)),
            today=date(2026, 5, 25),
        )

        self.assertEqual(signals[0]["label"], "Lleva tiempo aplicada")

    def test_technical_interview_and_offer_signals_use_expected_thresholds(self):
        technical = build_follow_up_signals(
            _application_item(1, status="Technical Test", application_date=date(2026, 5, 10)),
            today=date(2026, 5, 25),
        )
        interview = build_follow_up_signals(
            _application_item(2, status="In Interview", application_date=date(2026, 5, 10)),
            today=date(2026, 5, 25),
        )
        offer = build_follow_up_signals(
            _application_item(3, status="Open Offer", application_date=date(2026, 5, 10)),
            today=date(2026, 5, 25),
        )

        self.assertEqual(technical[0]["label"], "Lleva tiempo en prueba tecnica")
        self.assertEqual(interview[0]["label"], "Lleva tiempo en entrevista")
        self.assertEqual(offer[0]["label"], "Lleva tiempo en oferta")

    def test_missing_notes_and_contact_are_detected(self):
        signals = build_follow_up_signals(
            _application_item(1, status="Applied", notes="  "),
            today=date(2026, 5, 25),
        )

        labels = [signal["label"] for signal in signals]
        self.assertIn("Sin notas", labels)
        self.assertIn("Sin contacto", labels)

    def test_done_and_rejected_only_return_terminal_signal(self):
        done_signals = build_follow_up_signals(_application_item(1, status="Done"), today=date(2026, 5, 25))
        rejected_signals = build_follow_up_signals(
            _application_item(2, status="Rejected"),
            today=date(2026, 5, 25),
        )

        self.assertEqual(done_signals, [{"kind": "terminal", "label": "Terminal", "tone": "gray", "compact": False}])
        self.assertEqual(rejected_signals, [{"kind": "terminal", "label": "Terminal", "tone": "gray", "compact": False}])

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_renders_tracking_page(self, mock_repository, _mock_nav, _mock_metrics):
        item = _application_item(7, company="ACME", role="Data Analyst")
        item["notas"] = "Pendiente"
        mock_repository.list_all.return_value = [item]

        response = self.client.get("/app/applications")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Seguimiento", response.text)
        self.assertIn("ACME", response.text)
        self.assertIn("Pendiente por aplicar", response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[{"label": "Aplicaciones", "value": 42}])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_uses_compact_header_and_hides_global_metrics(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]

        response = self.client.get("/app/applications")

        self.assertEqual(response.status_code, 200)
        self.assertIn('<section class="page-header page-header-compact">', response.text)
        self.assertIn("<h1>Seguimiento</h1>", response.text)
        self.assertNotIn("Control simple de vacantes", response.text)
        self.assertNotIn('class="kpi-strip"', response.text)
        self.assertIn('id="applications-shell"', response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_update_status_hx_returns_shell_with_flash(self, mock_repository):
        mock_repository.update_status.return_value = {"success": True}
        items = [_application_item(item_id, status="Applied") for item_id in range(1, 26)]
        items[14]["notas"] = "Aplicada"
        mock_repository.list_all.return_value = items

        response = self.client.post(
            "/app/applications/15/status",
            data={
                "target_state": "Applied",
                "q": "acme",
                "state": "Applied",
                "page": "2",
                "page_size": "10",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("El estado de la aplicacion fue actualizado.", response.text)
        self.assertIn('value="2"', response.text)
        self.assertIn('value="10"', response.text)
        self.assertIn("/app/applications?selected=15&q=acme&state=Applied&page=2&page_size=10", response.text)
        mock_repository.update_status.assert_called_once_with(15, "Applied")

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_paginates_results(self, mock_repository, _mock_nav, _mock_metrics):
        mock_repository.list_all.return_value = [_application_item(item_id) for item_id in range(1, 26)]

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
        mock_repository.list_all.return_value = [_application_item(item_id) for item_id in range(1, 26)]

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
        mock_repository.list_all.return_value = [_application_item(item_id) for item_id in range(1, 26)]

        response = self.client.get("/app/applications?selected=25&page=1&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACME 25", response.text)
        self.assertIn("Pagina 3 de 3", response.text)
        self.assertIn('<h2>ACME 25</h2>', response.text)
        self.assertIn('class="application-role">Role 25</p>', response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_shell_uses_system_filter_button_and_preserves_shell_target(self, mock_repository):
        item = _application_item(7, company="ACME", role="Data Analyst")
        item["notas"] = "Pendiente"
        mock_repository.list_all.return_value = [item]

        response = self.client.get("/app/applications/shell?q=acme&state=Todos&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["HX-Push-Url"],
            "/app/applications?q=acme&state=Todos&page=1&page_size=20",
        )
        self.assertIn('id="applications-shell"', response.text)
        self.assertIn('class="workspace-toolbar"', response.text)
        self.assertIn('class="filter-form filter-form-compact"', response.text)
        self.assertIn('method="get"', response.text)
        self.assertIn('action="/app/applications"', response.text)
        self.assertIn('name="q"', response.text)
        self.assertIn('name="state"', response.text)
        self.assertIn('name="page_size"', response.text)
        self.assertIn('class="secondary-action filter-submit"', response.text)
        self.assertIn('hx-target="#applications-shell"', response.text)
        self.assertIn('hx-swap="outerHTML"', response.text)
        self.assertIn('hx-push-url="true"', response.text)
        self.assertIn('hx-get="/app/applications/shell"', response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_shell_selected_item_a_renders_matching_detail_and_selection(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME One", role="Role One"),
            _application_item(2, status="Applied", company="ACME Two", role="Role Two"),
        ]

        response = self.client.get("/app/applications/shell?selected=1&state=Todos&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["HX-Push-Url"],
            "/app/applications?selected=1&state=Todos&page=1&page_size=20",
        )
        self.assertIn('id="applications-shell"', response.text)
        self.assertIn("<h2>ACME One</h2>", response.text)
        self.assertIn('class="application-role">Role One</p>', response.text)
        self.assertIn(
            'class="row-link application-rail-row application-row state-gray is-selected"',
            response.text,
        )
        self.assertIn('id="application-detail"', response.text)
        self.assertIn('class="application-detail-panel"', response.text)
        self.assertIn('class="panel application-detail-sheet detail-sheet"', response.text)
        self.assertIn("/app/applications?selected=1&q=&state=Todos&page=1&page_size=20", response.text)
        self.assertIn(
            'hx-get="/app/applications/shell?selected=1&q=&state=Todos&page=1&page_size=20"',
            response.text,
        )
        self.assertIn(
            'hx-push-url="/app/applications?selected=1&q=&state=Todos&page=1&page_size=20"',
            response.text,
        )
        self.assertEqual(response.text.count('hx-push-url="true"'), 1)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_shell_selected_item_b_renders_matching_detail_and_selection(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME One", role="Role One"),
            _application_item(2, status="Applied", company="ACME Two", role="Role Two"),
        ]

        response = self.client.get("/app/applications/shell?selected=2&state=Todos&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["HX-Push-Url"],
            "/app/applications?selected=2&state=Todos&page=1&page_size=20",
        )
        self.assertIn('id="applications-shell"', response.text)
        self.assertIn("<h2>ACME Two</h2>", response.text)
        self.assertIn('class="application-role">Role Two</p>', response.text)
        self.assertIn(
            'class="row-link application-rail-row application-row state-blue is-selected"',
            response.text,
        )
        self.assertIn("/app/applications?selected=2&q=&state=Todos&page=1&page_size=20", response.text)
        self.assertIn(
            'hx-get="/app/applications/shell?selected=2&q=&state=Todos&page=1&page_size=20"',
            response.text,
        )
        self.assertIn(
            'hx-push-url="/app/applications?selected=2&q=&state=Todos&page=1&page_size=20"',
            response.text,
        )

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_list_groups_current_page_by_status_and_keeps_selection_links(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME Pending", role="Role Pending"),
            _application_item(2, status="Applied", company="ACME Applied", role="Role Applied"),
            _application_item(3, status="Rejected", company="ACME Rejected", role="Role Rejected"),
        ]

        response = self.client.get("/app/applications/shell?selected=2&q=acme&state=Todos&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="application-rail"', response.text)
        self.assertIn('class="list-section-label application-group-heading"', response.text)
        self.assertIn("ACME Pending", response.text)
        self.assertIn("ACME Applied", response.text)
        self.assertIn("ACME Rejected", response.text)
        self.assertIn("Lleva tiempo pendiente", response.text)
        self.assertIn("Lleva tiempo aplicada", response.text)
        self.assertIn("Seguimiento desde", response.text)
        self.assertIn('class="application-rail-id">#2</span>', response.text)
        self.assertIn("/app/applications?selected=2&q=acme&state=Todos&page=1&page_size=20", response.text)
        self.assertNotIn(">ID<", response.text)
        self.assertNotIn(">Empresa<", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_pending_rail_uses_neutral_tracking_date_copy_instead_of_aplicada(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME Pending", role="Role Pending"),
        ]

        response = self.client.get("/app/applications/shell?state=Pending&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Seguimiento desde", response.text)
        self.assertNotIn('<span class="application-rail-date-label">Aplicada</span>', response.text)
        self.assertIn("ACME Pending", response.text)
        self.assertIn("Role Pending", response.text)
        self.assertIn("Pendiente por aplicar", response.text)
        self.assertIn("Lleva tiempo pendiente", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_list_filtered_state_renders_single_group(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME Pending", role="Role Pending"),
            _application_item(2, status="Applied", company="ACME Applied", role="Role Applied"),
        ]

        response = self.client.get("/app/applications/shell?state=Applied&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn("ACME Applied", response.text)
        self.assertNotIn("ACME Pending", response.text)
        self.assertEqual(response.text.count('class="list-section-label application-group-heading"'), 1)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_partial_preserves_state_query_and_pagination(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(item_id) for item_id in range(1, 26)]

        response = self.client.get("/app/applications/25/detail?q=acme&state=Todos&page=3&page_size=10")

        self.assertEqual(response.status_code, 200)
        self.assertIn('<h2>ACME 25</h2>', response.text)
        self.assertIn('class="application-role">Role 25</p>', response.text)
        self.assertIn('value="acme"', response.text)
        self.assertIn('value="Todos"', response.text)
        self.assertIn('value="3"', response.text)
        self.assertIn('value="10"', response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_panel_prioritizes_operational_sections(self, mock_repository, _mock_nav, _mock_metrics):
        item = _application_item(7, company="ACME", role="Data Analyst")
        item["nombre_recruiter"] = "Ada"
        item["notas"] = "Pendiente de confirmar recruiter."
        mock_repository.list_all.return_value = [item]

        response = self.client.get("/app/applications")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Decision original", response.text)
        self.assertIn("Senales de seguimiento", response.text)
        self.assertIn("Accion principal", response.text)
        self.assertIn("Informacion de la aplicacion", response.text)
        self.assertIn("Contacto", response.text)
        self.assertIn("Notas", response.text)
        self.assertIn("Editar seguimiento", response.text)
        self.assertIn('class="primary-action application-primary-button"', response.text)
        self.assertIn('class="stack-form compact-form application-edit-form"', response.text)
        self.assertLess(response.text.index("Accion principal"), response.text.index("Editar seguimiento"))

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_batches_visible_vacancy_analysis_queries(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, company="ACME 1"),
            _application_item(2, company="ACME 2"),
        ]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {
            1: _analysis_item(score_total=93, decision_aplicacion="Aplicar si o si"),
            2: _analysis_item(score_total=64, decision_aplicacion="Aplicar si sobra tiempo"),
        }

        response = self.client.get("/app/applications?page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.mock_analysis_repository.get_by_vacancy_ids.assert_called_once_with([1, 2])
        self.mock_analysis_repository.get_by_vacancy_id.assert_not_called()

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_renders_original_decision_and_score(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {
            7: _analysis_item(
                score_total=88,
                decision_aplicacion="Aplicar si sobra tiempo",
                justificacion_decision="Buen match tecnico y alcance realista.",
            )
        }

        response = self.client.get("/app/applications?selected=7")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Decision original", response.text)
        self.assertIn("Aplicar si sobra tiempo", response.text)
        self.assertIn("Score 88", response.text)
        self.assertIn("Buen match tecnico y alcance realista.", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_uses_resumen_when_justification_is_missing(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {
            7: _analysis_item(
                score_total=74,
                decision_aplicacion="Aplicar",
                resumen_analisis="La vacante encaja con experiencia reciente.",
            )
        }

        response = self.client.get("/app/applications?selected=7")

        self.assertEqual(response.status_code, 200)
        self.assertIn("La vacante encaja con experiencia reciente.", response.text)
        self.assertIn("Justificacion", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_renders_original_strengths_and_risks(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {
            7: _analysis_item(
                score_total=81,
                decision_aplicacion="Aplicar",
                fortalezas_principales=["SQL fuerte", "Python aplicado"],
                riesgos_principales=["ETL no profundo"],
            )
        }

        response = self.client.get("/app/applications?selected=7")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Fortalezas", response.text)
        self.assertIn("SQL fuerte", response.text)
        self.assertIn("Riesgos", response.text)
        self.assertIn("ETL no profundo", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_shows_clean_fallback_when_analysis_is_missing(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {}

        response = self.client.get("/app/applications?selected=7")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Analisis original", response.text)
        self.assertIn("no tiene analisis original disponible", response.text)
        self.assertNotIn("Score 88", response.text)
        self.assertIn("Senales de seguimiento", response.text)
        self.assertIn("Lleva tiempo pendiente", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_list_shows_only_one_compact_signal_per_row(self, mock_repository):
        mock_repository.list_all.return_value = [
            _application_item(1, status="Pending", company="ACME Pending", role="Role Pending"),
        ]

        response = self.client.get("/app/applications/shell?selected=1&state=Todos&page=1&page_size=20")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.count('class="application-rail-signal"'), 1)
        self.assertEqual(response.text.count("Lleva tiempo pendiente"), 2)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_terminal_detail_does_not_render_operational_missing_info_signals(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, status="Done", company="ACME", role="Data Analyst")]

        response = self.client.get("/app/applications?selected=7&state=Done")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Senales de seguimiento", response.text)
        self.assertIn("Terminal", response.text)
        self.assertNotIn('<span class="status-badge status-gray">Sin notas</span>', response.text)
        self.assertNotIn('<span class="status-badge status-gray">Sin contacto</span>', response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_detail_handles_missing_score_or_decision_without_breaking(self, mock_repository):
        mock_repository.list_all.return_value = [_application_item(7, company="ACME", role="Data Analyst")]
        self.mock_analysis_repository.get_by_vacancy_ids.return_value = {
            7: _analysis_item(score_total=None, decision_aplicacion=None)
        }

        response = self.client.get("/app/applications?selected=7")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sin decision", response.text)
        self.assertIn("Score -", response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_applications_index_includes_done_in_filters_and_treats_it_as_terminal(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        mock_repository.list_all.return_value = [_application_item(7, status="Done")]

        response = self.client.get("/app/applications?state=Done")

        self.assertEqual(response.status_code, 200)
        self.assertIn('option value="Done" selected', response.text)
        self.assertIn("Cerrada", response.text)
        self.assertIn("estado terminal", response.text)
        self.assertNotIn("Ya aplique", response.text)
        self.assertNotIn("Paso a prueba tecnica", response.text)
        self.assertNotIn("Paso a entrevista", response.text)
        self.assertNotIn("Recibi oferta", response.text)
        self.assertNotIn("Marcar rechazada", response.text)
        self.assertIn("Editar seguimiento", response.text)

    @patch("app.interfaces.web.routes.applications._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.applications._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_rejected_application_is_terminal_and_delete_is_tertiary(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        mock_repository.list_all.return_value = [_application_item(7, status="Rejected")]

        response = self.client.get("/app/applications?state=Rejected")

        self.assertEqual(response.status_code, 200)
        self.assertIn("estado terminal", response.text)
        self.assertIn('class="tertiary-action"', response.text)
        self.assertNotIn("Marcar rechazada", response.text)
        self.assertNotIn('class="danger-action"', response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_update_status_redirect_preserves_context_in_classic_flow(self, mock_repository):
        mock_repository.update_status.return_value = {"success": True}

        response = self.client.post(
            "/app/applications/7/status",
            data={
                "target_state": "Done",
                "q": "acme",
                "state": "Applied",
                "page": "2",
                "page_size": "10",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/app/applications?selected=7&flash=status_updated&q=acme&state=Applied&page=2&page_size=10",
        )

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_update_application_redirect_preserves_context_in_classic_flow(self, mock_repository):
        mock_repository.update.return_value = {"success": True}

        response = self.client.post(
            "/app/applications/7/update",
            data={
                "estado": "Done",
                "nombre_recruiter": "Ada",
                "email_recruiter": "",
                "telefono_recruiter": "",
                "notas": "Cerrar seguimiento",
                "q": "acme",
                "state": "Pending",
                "page": "3",
                "page_size": "50",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/app/applications?selected=7&flash=application_updated&q=acme&state=Pending&page=3&page_size=50",
        )

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_update_application_hx_keeps_current_application_selected(self, mock_repository):
        mock_repository.update.return_value = {"success": True}
        items = [_application_item(item_id, status="Pending") for item_id in range(1, 26)]
        items[14]["notas"] = "Seguimiento actualizado"
        mock_repository.list_all.return_value = items

        response = self.client.post(
            "/app/applications/15/update",
            data={
                "estado": "Pending",
                "nombre_recruiter": "",
                "email_recruiter": "",
                "telefono_recruiter": "",
                "notas": "Seguimiento actualizado",
                "q": "acme",
                "state": "Pending",
                "page": "2",
                "page_size": "10",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Los datos de la aplicacion fueron actualizados.", response.text)
        self.assertIn('<h2>ACME 15</h2>', response.text)
        self.assertIn('class="application-role">Role 15</p>', response.text)
        self.assertIn("/app/applications?selected=15&q=acme&state=Pending&page=2&page_size=10", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_delete_application_redirect_preserves_context_in_classic_flow(self, mock_repository):
        mock_repository.delete.return_value = {"success": True}

        response = self.client.post(
            "/app/applications/7/delete",
            data={
                "q": "acme",
                "state": "Rejected",
                "page": "2",
                "page_size": "10",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/app/applications?selected=7&flash=application_deleted&q=acme&state=Rejected&page=2&page_size=10",
        )

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_delete_application_hx_reselects_first_visible_application(self, mock_repository):
        mock_repository.delete.return_value = {"success": True}
        mock_repository.list_all.return_value = [
            _application_item(8, status="Pending"),
            _application_item(9, status="Pending"),
        ]

        response = self.client.post(
            "/app/applications/7/delete",
            data={
                "q": "acme",
                "state": "Pending",
                "page": "1",
                "page_size": "10",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("La aplicacion fue eliminada.", response.text)
        self.assertIn('<h2>ACME 8</h2>', response.text)
        self.assertIn('class="application-role">Role 8</p>', response.text)
        self.assertIn("/app/applications?selected=8&q=acme&state=Pending&page=1&page_size=10", response.text)

    @patch("app.interfaces.web.routes.applications.application_repository")
    def test_delete_application_hx_falls_back_to_empty_state_when_list_is_empty(self, mock_repository):
        mock_repository.delete.return_value = {"success": True}
        mock_repository.list_all.return_value = []

        response = self.client.post(
            "/app/applications/7/delete",
            data={
                "q": "acme",
                "state": "Pending",
                "page": "1",
                "page_size": "10",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("La aplicacion fue eliminada.", response.text)
        self.assertIn("Sin coincidencias", response.text)
        self.assertIn("Sin detalle", response.text)
