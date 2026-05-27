"""Tests for the Perfil Laboral evidence inventory helper."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_evidence import build_profile_evidence_inventory


class ProfileEvidenceInventoryTests(unittest.TestCase):
    def test_inventory_calculates_counts_and_alerts_for_experiences_and_projects(self):
        inventory = build_profile_evidence_inventory(
            experiences=[
                {"es_trabajo_actual": True, "funciones": "Analisis", "logros": ""},
                {"es_trabajo_actual": False, "funciones": "", "logros": ""},
                {"es_trabajo_actual": False, "funciones": "", "logros": "Ahorro"},
            ],
            projects=[
                {"es_proyecto_actual": True, "stack": "Python, SQL", "funciones": "Dashboard", "logros": ""},
                {"es_proyecto_actual": False, "stack": "", "funciones": "", "logros": ""},
            ],
        )

        self.assertFalse(inventory.is_empty)
        self.assertEqual(inventory.total_items, 5)
        self.assertEqual(inventory.experiences.total, 3)
        self.assertEqual(inventory.experiences.current_count, 1)
        self.assertEqual(inventory.experiences.with_functions_count, 1)
        self.assertEqual(inventory.experiences.with_logros_count, 1)
        self.assertEqual(inventory.experiences.without_substance_count, 1)
        self.assertEqual(inventory.projects.total, 2)
        self.assertEqual(inventory.projects.current_count, 1)
        self.assertEqual(inventory.projects.with_stack_count, 1)
        self.assertEqual(inventory.projects.with_functions_count, 1)
        self.assertEqual(inventory.projects.with_logros_count, 0)
        self.assertEqual(inventory.projects.without_substance_count, 1)
        self.assertIn("experiencia(s) sin funciones ni logros", " ".join(inventory.alerts))
        self.assertIn("proyecto(s) sin descripcion ni logros", " ".join(inventory.alerts))

    def test_inventory_handles_empty_state(self):
        inventory = build_profile_evidence_inventory(experiences=[], projects=[])

        self.assertTrue(inventory.is_empty)
        self.assertEqual(inventory.total_items, 0)
        self.assertEqual(inventory.experiences.total, 0)
        self.assertEqual(inventory.projects.total, 0)
        self.assertIn("biblioteca de evidencia profesional", inventory.summary)
        self.assertIn("Aun no hay evidencia registrada", " ".join(inventory.alerts))


if __name__ == "__main__":
    unittest.main()
