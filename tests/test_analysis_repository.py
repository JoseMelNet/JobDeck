"""Tests for AnalysisRepository."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository


class AnalysisRepositoryTests(unittest.TestCase):
    def test_jdump_serializes_lists_and_dicts(self):
        self.assertEqual(AnalysisRepository._jdump([]), "[]")
        self.assertIn('"a": 1', AnalysisRepository._jdump({"a": 1}))

    def test_sjson_parses_json_or_returns_original_value(self):
        self.assertEqual(AnalysisRepository._sjson('["x"]'), ["x"])
        self.assertEqual(AnalysisRepository._sjson("plain"), "plain")
        self.assertEqual(AnalysisRepository._sjson(None), [])

    @patch("app.infrastructure.persistence.repositories.analysis_repository.get_connection")
    def test_get_by_vacancy_id_maps_saved_analysis(self, get_connection_mock):
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value = cursor
        cursor.fetchone.return_value = (
            80,
            79,
            "verde",
            "Senior",
            "ok",
            "Remoto",
            "$1000",
            "resumen",
            '["SQL"]',
            '["Python"]',
            '["SQL","Python"]',
            '["Comunicacion"]',
            '["English"]',
            "1000-2000",
            20,
            15,
            10,
            5,
            8,
            "Data",
            "Alta",
            "just",
            '["f1"]',
            '["r1"]',
            "encaje",
            "decision",
            "Aplicar",
            '["aj1"]',
            "2026-01-01",
        )
        get_connection_mock.return_value = conn
        repository = AnalysisRepository()

        result = repository.get_by_vacancy_id(1)

        self.assertEqual(result["score_total"], 80.0)
        self.assertEqual(result["skills_match"], ["SQL"])
        self.assertEqual(result["fortalezas_principales"], ["f1"])
        self.assertEqual(result["decision_aplicacion"], "Aplicar")


if __name__ == "__main__":
    unittest.main()
