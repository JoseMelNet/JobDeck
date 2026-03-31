"""Tests for AnalysisService."""

from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import Mock

from app.application.services.analysis_service import AnalysisService


class AnalysisServiceTests(unittest.TestCase):
    def test_returns_none_when_no_active_profile(self):
        repository = Mock()
        repository.get_active_profile.return_value = None
        service = AnalysisService(repository)

        result = service.build_profile_payload(1)

        self.assertIsNone(result)

    def test_builds_profile_payload(self):
        repository = Mock()
        repository.get_active_profile.return_value = {
            "id": 1,
            "nombre": "Ana",
            "titulo_profesional": "Data Analyst",
            "nivel_actual": "Senior",
            "anos_experiencia": 5,
            "salario_min": 1000,
            "salario_max": 2000,
            "moneda": "USD",
            "modalidades_aceptadas": "Remoto,Hibrido",
        }
        repository.get_skills.return_value = [{"categoria": "DB", "skill": "SQL", "nivel": "Avanzado"}]
        repository.get_experiences.return_value = [
            {
                "cargo": "Analyst",
                "empresa": "ACME",
                "fecha_inicio": date(2020, 1, 1),
                "fecha_fin": None,
                "es_trabajo_actual": True,
                "funciones": "Build reports",
                "logros": "Saved time",
            }
        ]
        repository.get_education.return_value = [
            {"titulo": "Systems", "institucion": "UNI", "nivel": "Pregrado", "status": "Completado"}
        ]
        repository.get_courses.return_value = [{"titulo": "Python", "institucion": "Coursera"}]
        repository.get_certifications.return_value = [{"titulo": "AWS", "institucion": "Amazon", "status": "Vigente"}]
        service = AnalysisService(repository)

        result = service.build_profile_payload(1)

        self.assertEqual(result["nombre"], "Ana")
        self.assertEqual(result["skills"][0]["skill"], "SQL")
        self.assertEqual(result["experiencias"][0]["fecha_fin"], "Actualidad")
        self.assertEqual(result["educacion"][0]["institucion"], "UNI")
        self.assertEqual(result["cursos"][0]["titulo"], "Python")
        self.assertEqual(result["certificaciones"][0]["status"], "Vigente")


if __name__ == "__main__":
    unittest.main()
