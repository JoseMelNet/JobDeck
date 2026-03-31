"""Tests for shared management styles."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from modules.components.ui_styles import MANAGEMENT_CSS, inject_management_styles


class UiStylesTests(unittest.TestCase):
    @patch("modules.components.ui_styles.st.markdown")
    def test_inject_management_styles_renders_css_once(self, markdown_mock):
        inject_management_styles()

        markdown_mock.assert_called_once_with(MANAGEMENT_CSS, unsafe_allow_html=True)


if __name__ == "__main__":
    unittest.main()
