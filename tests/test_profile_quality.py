"""Tests for the Perfil Laboral quality summary."""

from __future__ import annotations

from datetime import date
import unittest

from app.interfaces.web.presentation.profile_quality import build_profile_quality_summary
from app.interfaces.web.presentation.profile_view_model import ProfileSectionId


class ProfileQualitySummaryTests(unittest.TestCase):
    def test_quality_summary_prioritizes_objective_when_profile_is_missing(self):
        summary = build_profile_quality_summary(
            profile=None,
            skills=[],
            experiences=[],
            projects=[],
            education=[],
            courses=[],
            certifications=[],
        )

        self.assertEqual(summary.overall_label, "Perfil incompleto")
        self.assertEqual(summary.analysis_coverage.covered, 0)
        self.assertEqual(summary.cv_coverage.covered, 0)
        self.assertEqual(summary.evidence_coverage.covered, 0)
        self.assertEqual(summary.next_action.section_id, ProfileSectionId.OBJECTIVE)
        self.assertIn("titulo profesional", summary.next_action.description.lower())

    def test_quality_summary_uses_real_current_data_for_all_coverages(self):
        summary = build_profile_quality_summary(
            profile={
                "nombre": "Jose Mejia",
                "titulo_profesional": "Data Analyst",
                "ciudad": "Bogota",
                "correo": "jose@example.com",
                "perfil_linkedin": "https://linkedin.com/in/jose",
                "nivel_actual": "Senior",
                "anos_experiencia": 6,
                "salario_min": 8000000,
                "salario_max": 11000000,
                "modalidades_aceptadas": "Remoto,Hibrido",
            },
            skills=[{"categoria": "Data", "skill": "SQL", "nivel": "Avanzado"}],
            experiences=[
                {
                    "cargo": "Senior Data Analyst",
                    "empresa": "Acme",
                    "fecha_inicio": date(2022, 1, 1),
                    "fecha_fin": None,
                    "es_trabajo_actual": True,
                    "funciones": "Analisis de datos",
                    "logros": "Ahorro anual",
                }
            ],
            projects=[
                {
                    "nombre": "Forecasting",
                    "fecha_inicio": date(2024, 1, 1),
                    "fecha_fin": None,
                    "es_proyecto_actual": True,
                    "funciones": "Modelado",
                    "logros": "Redujo quiebres",
                }
            ],
            education=[{"titulo": "Ingenieria", "institucion": "UN"}],
            courses=[],
            certifications=[],
        )

        self.assertEqual(summary.analysis_coverage.percent, 100)
        self.assertEqual(summary.cv_coverage.percent, 100)
        self.assertEqual(summary.evidence_coverage.percent, 100)
        self.assertEqual(summary.overall_label, "Perfil consistente")
        self.assertEqual(summary.next_action.section_id, ProfileSectionId.OUTPUTS)

    def test_project_detail_counts_only_functions_or_logros(self):
        summary = build_profile_quality_summary(
            profile={
                "nombre": "Jose Mejia",
                "titulo_profesional": "Data Analyst",
                "ciudad": "Bogota",
                "correo": "jose@example.com",
                "perfil_linkedin": "https://linkedin.com/in/jose",
                "nivel_actual": "Mid",
                "anos_experiencia": 4,
                "salario_min": 5000000,
                "salario_max": 7000000,
                "modalidades_aceptadas": "Remoto",
            },
            skills=[{"categoria": "Data", "skill": "Python", "nivel": "Avanzado"}],
            experiences=[
                {
                    "cargo": "Data Analyst",
                    "empresa": "Acme",
                    "fecha_inicio": date(2023, 1, 1),
                    "fecha_fin": None,
                    "es_trabajo_actual": True,
                    "funciones": "Analisis",
                    "logros": None,
                }
            ],
            projects=[
                {
                    "nombre": "Dashboard",
                    "fecha_inicio": date(2024, 1, 1),
                    "fecha_fin": None,
                    "es_proyecto_actual": True,
                    "stack": "Python, SQL",
                    "funciones": None,
                    "logros": None,
                }
            ],
            education=[{"titulo": "Ingenieria", "institucion": "UN"}],
            courses=[],
            certifications=[],
        )

        self.assertEqual(summary.evidence_coverage.covered, 3)
        self.assertIn("Proyectos con funciones o logros", summary.evidence_coverage.gaps)
        self.assertIn("proyectos", " ".join(summary.alerts).lower())


if __name__ == "__main__":
    unittest.main()
