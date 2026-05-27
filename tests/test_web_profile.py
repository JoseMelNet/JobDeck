"""Tests for the web profile routes."""

from __future__ import annotations

from datetime import date
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class WebProfileTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    def _mock_empty_profile_workspace(self, mock_repository):
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

    def _mock_summary_ready_workspace(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose Mejia",
            "titulo_profesional": "Data Analyst",
            "ciudad": "Bogota",
            "correo": "jose@example.com",
            "perfil_linkedin": "https://linkedin.com/in/jose",
            "modalidades_aceptadas": "Remoto,Hibrido",
            "nivel_actual": "Mid",
            "anos_experiencia": 4,
            "salario_min": 5000000,
            "salario_max": 8000000,
            "moneda": "COP",
        }
        mock_repository.get_skills.return_value = [{"id": 1, "categoria": "Data", "skill": "SQL", "nivel": "Avanzado"}]
        mock_repository.get_experiences.return_value = [
            {
                "id": 10,
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2023, 1, 1),
                "fecha_fin": date(2024, 2, 1),
                "es_trabajo_actual": False,
                "funciones": "Analisis",
                "logros": "Ahorro",
            }
        ]
        mock_repository.get_projects.return_value = [
            {
                "id": 20,
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            }
        ]
        mock_repository.get_education.return_value = [
            {
                "id": 1,
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
                "fecha_fin": None,
            }
        ]
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

    def _mock_signals_inventory_workspace(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_skills.return_value = [
            {"id": 1, "categoria": "Data", "skill": "SQL", "nivel": "Avanzado"},
            {"id": 2, "categoria": "Data", "skill": " sql ", "nivel": "Intermedio"},
            {"id": 3, "categoria": "BI", "skill": "Power BI", "nivel": "Avanzado"},
            {"id": 4, "categoria": "", "skill": "Storytelling", "nivel": ""},
        ]

    def _mock_evidence_inventory_workspace(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_experiences.return_value = [
            {
                "id": 10,
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2023, 1, 1),
                "fecha_fin": None,
                "es_trabajo_actual": True,
                "funciones": "Analisis",
                "logros": "",
            },
            {
                "id": 11,
                "cargo": "BI Analyst",
                "empresa": "Globex",
                "ciudad": "Bogota",
                "descripcion_empresa": "CPG",
                "fecha_inicio": date(2021, 1, 1),
                "fecha_fin": date(2022, 12, 1),
                "es_trabajo_actual": False,
                "funciones": "",
                "logros": "",
            },
        ]
        mock_repository.get_projects.return_value = [
            {
                "id": 20,
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            },
            {
                "id": 21,
                "nombre": "Automation",
                "empresa": "",
                "ciudad": "Bogota",
                "fecha_inicio": date(2023, 6, 1),
                "fecha_fin": date(2023, 8, 1),
                "es_proyecto_actual": False,
                "stack": "",
                "funciones": "",
                "logros": "",
                "url_repositorio": "",
            },
        ]

    def _mock_credentials_inventory_workspace(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_education.return_value = [
            {
                "id": 1,
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
                "fecha_fin": None,
            },
            {
                "id": 2,
                "titulo": "Especializacion",
                "institucion": "",
                "nivel": "Especializacion",
                "status": "En curso",
                "fecha_inicio": "2025-01-01",
                "fecha_fin": None,
            },
        ]
        mock_repository.get_courses.return_value = [
            {
                "id": 3,
                "titulo": "SQL",
                "institucion": "Coursera",
                "status": "Completado",
                "url_certificado": "https://example.com/sql",
            },
            {
                "id": 4,
                "titulo": "Python",
                "institucion": "",
                "status": "En curso",
                "url_certificado": "",
            },
        ]
        mock_repository.get_certifications.return_value = [
            {
                "id": 5,
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
                "url_certificado": "",
            }
        ]

    def _mock_outputs_workspace(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose Mejia",
            "titulo_profesional": "Data Analyst",
            "ciudad": "Bogota",
            "correo": "jose@example.com",
            "celular": "3000000000",
            "perfil_linkedin": "https://linkedin.com/in/jose",
            "perfil_github": "https://github.com/jose",
            "modalidades_aceptadas": "Remoto,Hibrido",
            "nivel_actual": "Mid",
            "anos_experiencia": 4,
            "salario_min": 5000000,
            "salario_max": 8000000,
            "moneda": "COP",
        }
        mock_repository.get_skills.return_value = [
            {"id": 1, "categoria": "Data", "skill": "SQL", "nivel": "Avanzado"},
            {"id": 2, "categoria": "BI", "skill": "Power BI", "nivel": "Intermedio"},
        ]
        mock_repository.get_experiences.return_value = [
            {
                "id": 10,
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2023, 1, 1),
                "fecha_fin": None,
                "es_trabajo_actual": True,
                "funciones": "Analisis",
                "logros": "Ahorro",
            }
        ]
        mock_repository.get_projects.return_value = [
            {
                "id": 20,
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            }
        ]
        mock_repository.get_education.return_value = [
            {
                "id": 1,
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
                "fecha_fin": None,
            }
        ]
        mock_repository.get_courses.return_value = [
            {
                "id": 2,
                "titulo": "SQL",
                "institucion": "Coursera",
                "status": "Completado",
                "url_certificado": "https://example.com/sql",
            }
        ]
        mock_repository.get_certifications.return_value = [
            {
                "id": 3,
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
                "url_certificado": "",
            }
        ]

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_index_renders_profile_shell(self, mock_repository, _mock_nav, _mock_metrics):
        self._mock_empty_profile_workspace(mock_repository)

        response = self.client.get("/app/profile")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-shell"', response.text)
        self.assertIn("Perfil Laboral", response.text)
        self.assertIn("Resumen", response.text)
        self.assertIn("Objetivo", response.text)
        self.assertIn("Senales", response.text)
        self.assertIn("Salidas", response.text)
        self.assertIn("Calidad general del perfil", response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_shell_partial_renders_profile_sections(self, mock_repository):
        self._mock_empty_profile_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?flash=skill_added")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-shell"', response.text)
        self.assertIn("La skill fue agregada al perfil.", response.text)
        self.assertIn("Resumen", response.text)
        self.assertIn("Alertas principales", response.text)
        self.assertIn("Proxima accion recomendada", response.text)
        self.assertIn("Cobertura para analisis", response.text)
        self.assertNotIn("Estado de migracion", response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_evidence_section_renders_inventory_library(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_evidence_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile?section=evidence")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-evidence-shell"', response.text)
        self.assertIn("Biblioteca actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("Experiencias", response.text)
        self.assertIn("Proyectos", response.text)
        self.assertIn("2 experiencia(s) y 2 proyecto(s)", response.text)
        self.assertIn("sin funciones ni logros", response.text)
        self.assertIn("sin descripcion ni logros", response.text)
        self.assertIn("Con funciones: 1", response.text)
        self.assertIn("Con logros: 0", response.text)
        self.assertIn("Con stack: 1", response.text)
        self.assertIn("Data Analyst · Acme", response.text)
        self.assertIn("Automation", response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_evidence_shell_partial_renders_inventory_library(self, mock_repository):
        self._mock_evidence_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?section=evidence")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-evidence-shell"', response.text)
        self.assertIn("Biblioteca actual", response.text)
        self.assertIn("Experiencias", response.text)
        self.assertIn("Proyectos", response.text)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_credentials_section_renders_support_inventory(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_credentials_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile?section=credentials")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-credentials-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("2 educacion, 2 curso(s) y 1 certificacion(es)", response.text)
        self.assertIn("3 con institucion/emisor", response.text)
        self.assertIn("1 con soporte verificable", response.text)
        self.assertIn("credencial(es) con datos base incompletos", response.text)
        self.assertIn("Educacion", response.text)
        self.assertIn("Cursos", response.text)
        self.assertIn("Certificaciones", response.text)
        self.assertIn("Ingenieria", response.text)
        self.assertIn("SQL", response.text)
        self.assertIn("AWS", response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_credentials_shell_partial_renders_support_inventory(self, mock_repository):
        self._mock_credentials_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?section=credentials")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-credentials-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn('id="profile-formation-shell"', response.text)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_outputs_section_renders_base_cv_as_reusable_output(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_outputs_workspace(mock_repository)

        response = self.client.get("/app/profile?section=outputs")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-outputs-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("Datos de contacto y salida", response.text)
        self.assertIn("Estado del CV base", response.text)
        self.assertIn("Vista previa del CV base", response.text)
        self.assertIn("Salidas futuras", response.text)
        self.assertIn("CV base renderizable", response.text)
        self.assertIn("GitHub", response.text)
        self.assertIn("reutiliza el titulo profesional", response.text)
        self.assertIn('id="profile-cv-preview"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_outputs_shell_partial_keeps_inventory_and_cv_preview(self, mock_repository):
        self._mock_outputs_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?section=outputs")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-outputs-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("Vista previa del CV base", response.text)
        self.assertIn('id="profile-cv-preview"', response.text)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_workspace_supports_each_internal_section(self, mock_repository, _mock_nav, _mock_metrics):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_courses.return_value = [{"id": 2, "titulo": "SQL", "institucion": "Coursera", "status": "Completado"}]
        mock_repository.get_certifications.return_value = [
            {
                "id": 3,
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
            }
        ]

        expected = {
            "summary": 'id="profile-summary-shell"',
            "objective": 'id="profile-objective-shell"',
            "signals": 'id="profile-signals-shell"',
            "evidence": 'id="profile-evidence-shell"',
            "credentials": 'id="profile-credentials-shell"',
            "outputs": 'id="profile-outputs-shell"',
        }

        for section, marker in expected.items():
            with self.subTest(section=section):
                response = self.client.get(f"/app/profile?section={section}")
                self.assertEqual(response.status_code, 200)
                self.assertIn('id="profile-shell"', response.text)
                self.assertIn(marker, response.text)
                self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_shell_workspace_supports_each_internal_section(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_courses.return_value = [{"id": 2, "titulo": "SQL", "institucion": "Coursera", "status": "Completado"}]
        mock_repository.get_certifications.return_value = [
            {
                "id": 3,
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
            }
        ]

        expected = {
            "summary": 'id="profile-summary-shell"',
            "objective": 'id="profile-objective-shell"',
            "signals": 'id="profile-signals-shell"',
            "evidence": 'id="profile-evidence-shell"',
            "credentials": 'id="profile-credentials-shell"',
            "outputs": 'id="profile-outputs-shell"',
        }

        for section, marker in expected.items():
            with self.subTest(section=section):
                response = self.client.get(f"/app/profile/shell?section={section}")
                self.assertEqual(response.status_code, 200)
                self.assertIn('id="profile-shell"', response.text)
                self.assertIn(marker, response.text)
                self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_section_nav_uses_public_push_urls_and_shell_fetches(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)

        response = self.client.get("/app/profile?section=summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-shell"', response.text)
        for section in ("summary", "objective", "signals", "evidence", "credentials", "outputs"):
            with self.subTest(section=section):
                self.assertIn(f'href="/app/profile?section={section}"', response.text)
                self.assertIn(f'hx-get="/app/profile/shell?section={section}"', response.text)
                self.assertIn('hx-target="#profile-shell"', response.text)
                self.assertIn('hx-swap="outerHTML"', response.text)
                self.assertIn(f'hx-push-url="/app/profile?section={section}"', response.text)

        self.assertNotIn('hx-push-url="true"', response.text)
        self.assertNotIn('hx-push-url="/app/profile/shell?', response.text)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_summary_section_renders_quality_command_center(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_summary_ready_workspace(mock_repository)

        response = self.client.get("/app/profile?section=summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Calidad general del perfil", response.text)
        self.assertIn("Cobertura para analisis", response.text)
        self.assertIn("Cobertura para CV base", response.text)
        self.assertIn("Cobertura de evidencia", response.text)
        self.assertIn("Proxima accion recomendada", response.text)
        self.assertIn("Alertas principales", response.text)
        self.assertIn("Limites actuales", response.text)
        self.assertNotIn("Como usar esta pantalla", response.text)
        self.assertNotIn("Vista CV", response.text)
        self.assertNotIn("Estado de migracion", response.text)
        self.assertIn('href="/app/profile?section=outputs"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_summary_shell_partial_keeps_navigation_and_quality(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?section=summary")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("Calidad general del perfil", response.text)
        self.assertIn("Proxima accion recomendada", response.text)
        self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_objective_section_prioritizes_strategy_over_contact(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_active_profile.return_value["celular"] = "3001234567"
        mock_repository.get_active_profile.return_value["perfil_github"] = "https://github.com/jose"

        response = self.client.get("/app/profile?section=objective")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-objective-shell"', response.text)
        self.assertIn("Objetivo laboral", response.text)
        self.assertIn("Base estrategica", response.text)
        self.assertIn("Condiciones de busqueda", response.text)
        self.assertIn("Contacto y salida", response.text)
        self.assertIn("Titulo profesional", response.text)
        self.assertIn("Modalidades aceptadas", response.text)
        self.assertIn("GitHub", response.text)
        self.assertIn("comparas vacantes", response.text.lower())

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_objective_shell_partial_keeps_strategic_groups(self, mock_repository):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_active_profile.return_value["celular"] = "3001234567"

        response = self.client.get("/app/profile/shell?section=objective")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-objective-shell"', response.text)
        self.assertIn("Base estrategica y datos de salida", response.text)
        self.assertIn("Base estrategica", response.text)
        self.assertIn("Condiciones de busqueda", response.text)
        self.assertIn("Contacto y salida", response.text)
        self.assertEqual(response.text.count('aria-current="page"'), 1)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_signals_section_keeps_focus_on_skills_without_global_status(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_signals_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile?section=signals")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-signals-shell"', response.text)
        self.assertIn("Senales de afinidad", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Agregar skill", response.text)
        self.assertIn("Data", response.text)
        self.assertIn("BI", response.text)
        self.assertIn("Sin categoria", response.text)
        self.assertIn("Posible duplicado", response.text)
        self.assertNotIn("Estado del perfil", response.text)
        self.assertNotIn("Alertas principales", response.text)
        self.assertNotIn("Estado de migracion", response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_signals_shell_partial_renders_inventory_groups(self, mock_repository):
        self._mock_signals_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile/shell?section=signals")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-signals-shell"', response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("SQL x2", response.text)

    @patch("app.interfaces.web.routes.profile._build_metrics", return_value=[])
    @patch("app.interfaces.web.routes.profile._build_nav", return_value=[])
    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_signals_section_supports_empty_inventory_state(
        self,
        mock_repository,
        _mock_nav,
        _mock_metrics,
    ):
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_skills.return_value = []

        response = self.client.get("/app/profile?section=signals")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sin skills", response.text)
        self.assertIn("Aun no hay un inventario de senales", response.text)
        self.assertIn("Agregar skill", response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_skills_partial_renders_isolated_skills_shell(self, mock_repository):
        self._mock_signals_inventory_workspace(mock_repository)

        response = self.client.get("/app/profile/skills")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn("SQL", response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Revision rapida", response.text)
        self.assertIn("Agregar skill", response.text)
        self.assertNotIn("Estado del perfil", response.text)
        self.assertNotIn("Alertas principales", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_basics_partial_renders_isolated_basics_shell(self, mock_repository):
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

        response = self.client.get("/app/profile/basics")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-basics-shell"', response.text)
        self.assertIn("Datos principales", response.text)
        self.assertIn('action="/app/profile/save"', response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_save_profile_hx_returns_isolated_basics_fragment(self, mock_repository):
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
        self.assertIn('id="profile-basics-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertNotIn('action="/app/profile/experiences"', response.text)
        payload = mock_repository.save_profile.call_args.args[0]
        self.assertEqual(payload["modalidades_aceptadas"], "Remoto,Hibrido")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_save_profile_non_hx_redirects_to_objective_section(self, mock_repository):
        mock_repository.save_profile.return_value = {"success": True, "id": 1}

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
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/app/profile?section=objective&flash=profile_saved")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_skill_hx_returns_isolated_skills_fragment(self, mock_repository):
        mock_repository.add_skill.return_value = {"success": True}
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_skills.return_value = [{"id": 2, "categoria": "Data", "skill": "Python", "nivel": "Avanzado"}]

        response = self.client.post(
            "/app/profile/skills",
            data={"categoria": "Data", "skill": "Python", "nivel": "Avanzado"},
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertIn("La skill fue agregada al perfil.", response.text)
        self.assertIn("Inventario actual", response.text)
        self.assertIn("Agregar skill", response.text)
        self.assertIn("Python", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_skill_non_hx_redirects_to_signals_section(self, mock_repository):
        mock_repository.add_skill.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {"id": 1}

        response = self.client.post(
            "/app/profile/skills",
            data={"categoria": "Data", "skill": "Python", "nivel": "Avanzado"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/app/profile?section=signals&flash=skill_added")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_skill_hx_returns_isolated_skills_fragment(self, mock_repository):
        mock_repository.delete_skill.return_value = {"success": True}
        self._mock_summary_ready_workspace(mock_repository)
        mock_repository.get_skills.return_value = []

        response = self.client.post(
            "/app/profile/skills/2/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn("La skill fue eliminada.", response.text)
        self.assertIn("Sin skills", response.text)
        self.assertIn("Aun no hay un inventario de senales", response.text)
        self.assertIn("Agregar skill", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_experience_non_hx_redirects_to_evidence_section(self, mock_repository):
        mock_repository.add_experience.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {"id": 1}

        response = self.client.post(
            "/app/profile/experiences",
            data={
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "fecha_inicio": "2024-01-01",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/app/profile?section=evidence&flash=experience_saved")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_education_non_hx_redirects_to_credentials_section(self, mock_repository):
        mock_repository.add_education.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {"id": 1}

        response = self.client.post(
            "/app/profile/education",
            data={
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/app/profile?section=credentials&flash=education_saved")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_shell_partial_keeps_formation_sections(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile/shell?section=credentials")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Educacion", response.text)
        self.assertIn("Cursos", response.text)
        self.assertIn("Certificaciones", response.text)
        self.assertIn('action="/app/profile/education"', response.text)
        self.assertIn('action="/app/profile/courses"', response.text)
        self.assertIn('action="/app/profile/certifications"', response.text)
        self.assertIn('id="profile-credentials-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_shell_partial_renders_experience_and_project_records(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = [
            {
                "id": 10,
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2023, 1, 1),
                "fecha_fin": date(2024, 2, 1),
                "es_trabajo_actual": False,
                "funciones": "Analisis",
                "logros": "Ahorro",
            }
        ]
        mock_repository.get_projects.return_value = [
            {
                "id": 20,
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            }
        ]
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile/shell?section=evidence")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Experiencia", response.text)
        self.assertIn("Data Analyst · Acme", response.text)
        self.assertIn('action="/app/profile/experiences/10/update"', response.text)
        self.assertIn('action="/app/profile/experiences/10/delete"', response.text)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn("Proyectos", response.text)
        self.assertIn("Dashboard", response.text)
        self.assertIn('action="/app/profile/projects/20/update"', response.text)
        self.assertIn('action="/app/profile/projects/20/delete"', response.text)
        self.assertIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_formation_partial_renders_isolated_formation_shell(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile/formation")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn("Educacion", response.text)
        self.assertIn("Cursos", response.text)
        self.assertIn("Certificaciones", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertNotIn('id="profile-basics-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_projects_partial_renders_isolated_projects_shell(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile/projects")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-projects-shell"', response.text)
        self.assertIn("Proyectos", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertNotIn('id="profile-basics-shell"', response.text)
        self.assertNotIn('id="profile-cv-preview"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_experiences_partial_renders_isolated_experiences_shell(self, mock_repository):
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.get("/app/profile/experiences")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn("Experiencia", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertNotIn('id="profile-basics-shell"', response.text)
        self.assertNotIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_project_hx_returns_isolated_projects_fragment(self, mock_repository):
        mock_repository.add_project.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = [
            {
                "id": 4,
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            }
        ]
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/projects",
            data={
                "nombre": "Dashboard",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": "2024-01-01",
                "stack": "Python, SQL",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-projects-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("El proyecto fue guardado.", response.text)
        self.assertIn("Dashboard", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertNotIn('id="profile-cv-preview"', response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_update_project_hx_returns_isolated_projects_fragment(self, mock_repository):
        mock_repository.update_project.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = [
            {
                "id": 4,
                "nombre": "Dashboard V2",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_proyecto_actual": True,
                "stack": "Python, SQL",
                "funciones": "Construccion",
                "logros": "Visibilidad",
                "url_repositorio": "https://example.com/repo",
            }
        ]
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/projects/4/update",
            data={
                "nombre": "Dashboard V2",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": "2024-01-01",
                "es_proyecto_actual": "true",
                "stack": "Python, SQL",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-projects-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("El proyecto fue guardado.", response.text)
        self.assertIn("Dashboard V2", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertNotIn('id="profile-cv-preview"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_experience_hx_returns_isolated_experiences_fragment(self, mock_repository):
        mock_repository.add_experience.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = [
            {
                "id": 6,
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_trabajo_actual": True,
                "funciones": "Analisis",
                "logros": "Impacto",
            }
        ]
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/experiences",
            data={
                "cargo": "Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": "2024-01-01",
                "es_trabajo_actual": "true",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La experiencia fue guardada.", response.text)
        self.assertIn("Data Analyst · Acme", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertNotIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_update_experience_hx_returns_isolated_experiences_fragment(self, mock_repository):
        mock_repository.update_experience.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = [
            {
                "id": 6,
                "cargo": "Senior Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "descripcion_empresa": "Retail",
                "fecha_inicio": date(2024, 1, 1),
                "fecha_fin": None,
                "es_trabajo_actual": True,
                "funciones": "Analisis",
                "logros": "Impacto",
            }
        ]
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/experiences/6/update",
            data={
                "cargo": "Senior Data Analyst",
                "empresa": "Acme",
                "ciudad": "Bogota",
                "fecha_inicio": "2024-01-01",
                "es_trabajo_actual": "true",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La experiencia fue guardada.", response.text)
        self.assertIn("Senior Data Analyst · Acme", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertNotIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_experience_hx_returns_isolated_experiences_fragment(self, mock_repository):
        mock_repository.delete_experience.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/experiences/6/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-experiences-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La experiencia fue eliminada.", response.text)
        self.assertIn("Sin experiencia registrada", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertNotIn('id="profile-projects-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_project_hx_returns_isolated_projects_fragment(self, mock_repository):
        mock_repository.delete_project.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/projects/4/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-projects-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("El proyecto fue eliminado.", response.text)
        self.assertIn("Sin proyectos registrados", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertNotIn('id="profile-cv-preview"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_education_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.add_education.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = [
            {
                "id": 1,
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
                "fecha_fin": None,
            }
        ]
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/education",
            data={
                "titulo": "Ingenieria",
                "institucion": "UN",
                "nivel": "Pregrado",
                "status": "Completado",
                "fecha_inicio": "2020-01-01",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La educacion fue guardada.", response.text)
        self.assertNotIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertNotIn('action="/app/profile/experiences"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_education_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.delete_education.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/education/1/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La educacion fue eliminada.", response.text)
        self.assertIn("Sin educacion registrada", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_course_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.add_course.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = [{"id": 2, "titulo": "SQL", "institucion": "Coursera", "status": "Completado"}]
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/courses",
            data={
                "titulo": "SQL",
                "institucion": "Coursera",
                "status": "Completado",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("El curso fue guardado.", response.text)
        self.assertIn("SQL", response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_course_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.delete_course.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/courses/2/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("El curso fue eliminado.", response.text)
        self.assertIn("Sin cursos registrados", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_certification_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.add_certification.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = [
            {
                "id": 3,
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
            }
        ]

        response = self.client.post(
            "/app/profile/certifications",
            data={
                "titulo": "AWS",
                "institucion": "AWS",
                "status": "Vigente",
                "fecha_obtencion": "2024-01-01",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La certificacion fue guardada.", response.text)
        self.assertIn("AWS", response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_certification_hx_returns_isolated_formation_fragment(self, mock_repository):
        mock_repository.delete_certification.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = []
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/certifications/3/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-formation-shell"', response.text)
        self.assertIn('id="profile-summary-shell"', response.text)
        self.assertIn("La certificacion fue eliminada.", response.text)
        self.assertIn("Sin certificaciones registradas", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)
