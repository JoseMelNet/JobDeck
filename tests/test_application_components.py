"""Tests for application UI components."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from modules.components.application_components import render_application_detail_summary


class ApplicationComponentsTests(unittest.TestCase):
    @patch("modules.components.application_components.st.divider")
    @patch("modules.components.application_components.st.markdown")
    def test_render_application_detail_summary_renders_summary_blocks(self, markdown_mock, divider_mock):
        app_item = {
            "id": 3,
            "modalidad": "Remoto",
            "link": "https://example.com/app",
            "nombre_recruiter": "Ana",
            "email_recruiter": "ana@example.com",
            "telefono_recruiter": "123",
        }

        render_application_detail_summary(
            app_item,
            modalidad_meta={"emoji": "remoto", "color": "#000"},
            fecha_str="01/03/2026",
        )

        self.assertEqual(markdown_mock.call_count, 3)
        self.assertIn("info-grid cols-4", markdown_mock.call_args_list[0].args[0])
        self.assertIn("https://example.com/app", markdown_mock.call_args_list[1].args[0])
        self.assertIn("Recruiter", markdown_mock.call_args_list[2].args[0])
        divider_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
