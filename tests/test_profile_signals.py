"""Tests for the Perfil Laboral signals inventory helper."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_signals import build_profile_signals_inventory


class ProfileSignalsInventoryTests(unittest.TestCase):
    def test_inventory_groups_by_category_and_flags_duplicates_and_missing_fields(self):
        inventory = build_profile_signals_inventory(
            [
                {"id": 1, "categoria": "Data", "skill": " SQL ", "nivel": "Avanzado"},
                {"id": 2, "categoria": "Data", "skill": "sql", "nivel": "Intermedio"},
                {"id": 3, "categoria": "BI", "skill": "Power BI", "nivel": "Basico"},
                {"id": 4, "categoria": "", "skill": "Storytelling", "nivel": ""},
            ]
        )

        self.assertFalse(inventory.is_empty)
        self.assertEqual(inventory.total_skills, 4)
        self.assertEqual(inventory.category_count, 2)
        self.assertEqual(inventory.uncategorized_count, 1)
        self.assertEqual(inventory.without_level_count, 1)
        self.assertEqual(inventory.duplicate_count, 1)
        self.assertEqual(inventory.categories_present, ("BI", "Data"))
        self.assertEqual(inventory.group_by_label("Data").count, 2)
        self.assertEqual(inventory.group_by_label("Sin categoria").skills[0].level_label, "Nivel no indicado")
        self.assertTrue(any(item.is_duplicate for item in inventory.group_by_label("Data").skills))
        self.assertEqual(inventory.duplicate_skills[0].name, "SQL")
        self.assertIn("sin categoria", " ".join(inventory.alerts).lower())
        self.assertIn("duplicado", " ".join(inventory.alerts).lower())

    def test_inventory_handles_empty_state(self):
        inventory = build_profile_signals_inventory([])

        self.assertTrue(inventory.is_empty)
        self.assertEqual(inventory.total_skills, 0)
        self.assertEqual(inventory.groups, ())
        self.assertEqual(inventory.duplicate_skills, ())
        self.assertIn("Aun no has registrado skills", inventory.summary)


if __name__ == "__main__":
    unittest.main()
