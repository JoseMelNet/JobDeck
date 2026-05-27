"""Tests for the Perfil Laboral outputs inventory helper."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_outputs import build_profile_outputs_inventory


class ProfileOutputsInventoryTests(unittest.TestCase):
    def test_inventory_calculates_contact_cv_state_and_current_limits(self):
        inventory = build_profile_outputs_inventory(
            profile={
                "nombre": "Jose Mejia",
                "titulo_profesional": "Data Analyst",
                "correo": "jose@example.com",
                "ciudad": "Bogota",
                "celular": "3000000000",
                "perfil_linkedin": "https://linkedin.com/in/jose",
                "perfil_github": "https://github.com/jose",
            },
            skills=[{"skill": "SQL"}],
            experiences=[{"cargo": "Data Analyst"}],
            education=[{"titulo": "Ingenieria"}],
            courses=[],
            certifications=[],
            cv_preview_html="<div>cv</div>",
        )

        self.assertFalse(inventory.is_empty)
        self.assertEqual(inventory.contact.ready_count, 6)
        self.assertTrue(inventory.cv_base.is_renderable)
        self.assertEqual(inventory.cv_base.ready_count, 9)
        self.assertTrue(inventory.cv_base.uses_title_as_summary)
        self.assertIn("CV base", inventory.summary)
        self.assertIn("titulo profesional", " ".join(inventory.limits).lower())
        self.assertIn("github", " ".join(inventory.limits).lower())

    def test_inventory_handles_empty_state_without_profile(self):
        inventory = build_profile_outputs_inventory(
            profile=None,
            skills=[],
            experiences=[],
            education=[],
            courses=[],
            certifications=[],
            cv_preview_html=None,
        )

        self.assertTrue(inventory.is_empty)
        self.assertEqual(inventory.contact.ready_count, 0)
        self.assertFalse(inventory.cv_base.is_renderable)
        self.assertEqual(inventory.cv_base.ready_count, 0)
        self.assertIn("salida reusable", inventory.summary.lower())
        self.assertIn("Aun no hay datos suficientes", " ".join(inventory.alerts))


if __name__ == "__main__":
    unittest.main()
