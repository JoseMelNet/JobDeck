"""Tests for shared UI labels and normalization helpers."""

from __future__ import annotations

import unittest

from modules.components.ui_labels import normalize_modality_label


class NormalizeModalityLabelTests(unittest.TestCase):
    def test_returns_dash_for_empty_values(self):
        self.assertEqual(normalize_modality_label(None), "-")
        self.assertEqual(normalize_modality_label(""), "-")

    def test_normalizes_hybrid_variants(self):
        self.assertEqual(normalize_modality_label("Hibrido"), "Hibrido")
        self.assertEqual(normalize_modality_label("H\u00edbrido"), "Hibrido")
        self.assertEqual(normalize_modality_label("H\u00c3\u00adbrido"), "Hibrido")

    def test_keeps_known_simple_labels(self):
        self.assertEqual(normalize_modality_label("Remoto"), "Remoto")
        self.assertEqual(normalize_modality_label("Presencial"), "Presencial")


if __name__ == "__main__":
    unittest.main()
