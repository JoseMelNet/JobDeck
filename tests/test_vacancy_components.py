"""Tests for vacancy UI components."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from modules.components.vacancy_components import render_vacancy_detail_summary


class VacancyComponentsTests(unittest.TestCase):
    @patch("modules.components.vacancy_components.st.markdown")
    def test_render_vacancy_detail_summary_renders_cards_and_link(self, markdown_mock):
        vacante = {
            "id": 7,
            "empresa": "ACME",
            "cargo": "Data Analyst",
            "modalidad": "Remoto",
            "fecha_registro": None,
            "motivo_archivo": None,
            "link": "https://example.com/job",
        }

        render_vacancy_detail_summary(
            vacante,
            archivada=False,
            modalidades_emoji={"Remoto": "Remoto"},
        )

        self.assertEqual(markdown_mock.call_count, 2)
        first_call = markdown_mock.call_args_list[0]
        second_call = markdown_mock.call_args_list[1]
        self.assertIn("info-grid", first_call.args[0])
        self.assertIn("Data Analyst", first_call.args[0])
        self.assertEqual(first_call.kwargs, {"unsafe_allow_html": True})
        self.assertIn("https://example.com/job", second_call.args[0])


if __name__ == "__main__":
    unittest.main()
