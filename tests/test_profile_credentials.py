"""Tests for the Perfil Laboral credentials inventory helper."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_credentials import build_profile_credentials_inventory


class ProfileCredentialsInventoryTests(unittest.TestCase):
    def test_inventory_calculates_totals_support_and_incomplete_credentials(self):
        inventory = build_profile_credentials_inventory(
            education=[
                {"titulo": "Ingenieria", "institucion": "UN", "nivel": "Pregrado"},
                {"titulo": "Especializacion", "institucion": "", "nivel": "Especializacion"},
            ],
            courses=[
                {"titulo": "SQL", "institucion": "Coursera", "url_certificado": "https://example.com/sql"},
                {"titulo": "Python", "institucion": "", "url_certificado": ""},
            ],
            certifications=[
                {"titulo": "AWS", "institucion": "AWS", "url_certificado": ""},
            ],
        )

        self.assertFalse(inventory.is_empty)
        self.assertEqual(inventory.total_credentials, 5)
        self.assertEqual(inventory.education.total, 2)
        self.assertEqual(inventory.courses.total, 2)
        self.assertEqual(inventory.certifications.total, 1)
        self.assertEqual(inventory.with_issuer_total, 3)
        self.assertEqual(inventory.with_url_total, 1)
        self.assertEqual(inventory.incomplete_total, 2)
        self.assertIn("institucion o emisor", " ".join(inventory.alerts).lower())
        self.assertIn("url", " ".join(inventory.alerts).lower())

    def test_inventory_handles_empty_state(self):
        inventory = build_profile_credentials_inventory([], [], [])

        self.assertTrue(inventory.is_empty)
        self.assertEqual(inventory.total_credentials, 0)
        self.assertEqual(inventory.with_issuer_total, 0)
        self.assertEqual(inventory.with_url_total, 0)
        self.assertIn("soporte profesional", inventory.summary)
        self.assertIn("Aun no hay credenciales registradas", " ".join(inventory.alerts))


if __name__ == "__main__":
    unittest.main()
