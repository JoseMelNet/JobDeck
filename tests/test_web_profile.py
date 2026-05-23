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
    def test_profile_shell_partial_renders_profile_sections(self, mock_repository):
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

        response = self.client.get("/app/profile/shell?flash=skill_added")

        self.assertEqual(response.status_code, 200)
        self.assertIn("La skill fue agregada al perfil.", response.text)
        self.assertIn("Datos principales", response.text)
        self.assertIn("Estado del perfil", response.text)
        self.assertIn("Vista CV", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_profile_skills_partial_renders_isolated_skills_shell(self, mock_repository):
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

        response = self.client.get("/app/profile/skills")

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn("SQL", response.text)
        self.assertIn("Estado del perfil", response.text)
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
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="outerHTML"', response.text)
        self.assertNotIn('action="/app/profile/experiences"', response.text)
        payload = mock_repository.save_profile.call_args.args[0]
        self.assertEqual(payload["modalidades_aceptadas"], "Remoto,Hibrido")

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_add_skill_hx_returns_isolated_skills_fragment(self, mock_repository):
        mock_repository.add_skill.return_value = {"success": True}
        mock_repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Jose",
            "titulo_profesional": "Data Analyst",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        mock_repository.get_skills.return_value = [{"id": 2, "categoria": "Data", "skill": "Python", "nivel": "Avanzado"}]
        mock_repository.get_experiences.return_value = []
        mock_repository.get_projects.return_value = []
        mock_repository.get_education.return_value = []
        mock_repository.get_courses.return_value = []
        mock_repository.get_certifications.return_value = []

        response = self.client.post(
            "/app/profile/skills",
            data={"categoria": "Data", "skill": "Python", "nivel": "Avanzado"},
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn('hx-swap-oob="innerHTML"', response.text)
        self.assertIn("La skill fue agregada al perfil.", response.text)
        self.assertIn("Python", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

    @patch("app.interfaces.web.routes.profile.profile_repository")
    def test_delete_skill_hx_returns_isolated_skills_fragment(self, mock_repository):
        mock_repository.delete_skill.return_value = {"success": True}
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
            "/app/profile/skills/2/delete",
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn("La skill fue eliminada.", response.text)
        self.assertIn("Sin skills", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)

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

        response = self.client.get("/app/profile/shell")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Educacion", response.text)
        self.assertIn("Cursos", response.text)
        self.assertIn("Certificaciones", response.text)
        self.assertIn('action="/app/profile/education"', response.text)
        self.assertIn('action="/app/profile/courses"', response.text)
        self.assertIn('action="/app/profile/certifications"', response.text)

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

        response = self.client.get("/app/profile/shell")

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
        self.assertIn("El proyecto fue guardado.", response.text)
        self.assertIn("Dashboard", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("El proyecto fue guardado.", response.text)
        self.assertIn("Dashboard V2", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("La experiencia fue guardada.", response.text)
        self.assertIn("Data Analyst · Acme", response.text)
        self.assertIn('id="profile-overview"', response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
        self.assertIn('id="profile-cv-preview"', response.text)
        self.assertIn('hx-swap-oob="innerHTML"', response.text)
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
        self.assertIn("La experiencia fue guardada.", response.text)
        self.assertIn("Senior Data Analyst · Acme", response.text)
        self.assertIn('id="profile-overview"', response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("La experiencia fue eliminada.", response.text)
        self.assertIn("Sin experiencia registrada", response.text)
        self.assertIn('id="profile-overview"', response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("El proyecto fue eliminado.", response.text)
        self.assertIn("Sin proyectos registrados", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("La educacion fue guardada.", response.text)
        self.assertIn('id="profile-skills-shell"', response.text)
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
        self.assertIn("La certificacion fue eliminada.", response.text)
        self.assertIn("Sin certificaciones registradas", response.text)
        self.assertNotIn('action="/app/profile/save"', response.text)
