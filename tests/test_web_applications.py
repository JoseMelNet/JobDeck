"""Tests for the web applications routes."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


def _application_item(
    item_id: int,
    *,
    status: str = "Pending",
    company: str | None = None,
    role: str | None = None,
) -> dict:
    return {
        "id": item_id,
        "vacante_id": item_id,
        "empresa": company or f"ACME {item_id}",
        "cargo": role or f"Role {item_id}",
        "modalidad": "Remoto",
        "link": "https://example.com",
        "fecha_aplicacion": date(2026, 4, 1),
        "estado": status,
        "nombre_recruiter": None,
        "email_recruiter": None,
        "telefono_recruiter": None,
        "notas": "",
        "fecha_registro": date(2026, 4, 1),
    }


class WebApplicationsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

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
        self.assertIn('class="secondary-action filter-submit"', response.text)
        self.assertIn('hx-target="#applications-shell"', response.text)
        self.assertIn('hx-swap="outerHTML"', response.text)
        self.assertIn('hx-push-url="true"', response.text)

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
        self.assertIn("Accion principal", response.text)
        self.assertIn("Informacion de la aplicacion", response.text)
        self.assertIn("Contacto", response.text)
        self.assertIn("Notas", response.text)
        self.assertIn("Editar seguimiento", response.text)
        self.assertIn('class="primary-action application-primary-button"', response.text)
        self.assertIn('class="stack-form compact-form application-edit-form"', response.text)
        self.assertLess(response.text.index("Accion principal"), response.text.index("Editar seguimiento"))

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
