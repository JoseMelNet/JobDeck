"""Tests for the Perfil Laboral refresh contract."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_refresh import (
    ProfileRefreshAction,
    build_profile_refresh_plan,
)
from app.interfaces.web.presentation.profile_view_model import ProfileSectionId


class ProfileRefreshContractTests(unittest.TestCase):
    def test_basics_refreshes_summary_signals_and_cv(self):
        plan = build_profile_refresh_plan(ProfileRefreshAction.BASICS)

        self.assertEqual(plan.primary_template, "profile/_basics.html")
        self.assertEqual(plan.redirect_section, ProfileSectionId.OBJECTIVE)
        self.assertTrue(plan.refresh_summary)
        self.assertTrue(plan.refresh_signals)
        self.assertTrue(plan.refresh_cv_preview)

    def test_skills_refreshes_summary_and_cv_without_duplicate_signals_oob(self):
        plan = build_profile_refresh_plan(ProfileRefreshAction.SKILLS)

        self.assertEqual(plan.primary_template, "profile/_skills_shell.html")
        self.assertEqual(plan.redirect_section, ProfileSectionId.SIGNALS)
        self.assertTrue(plan.refresh_summary)
        self.assertFalse(plan.refresh_signals)
        self.assertTrue(plan.refresh_cv_preview)

    def test_projects_refreshes_summary_without_cv_preview(self):
        plan = build_profile_refresh_plan(ProfileRefreshAction.PROJECTS)

        self.assertEqual(plan.primary_template, "profile/_projects_shell.html")
        self.assertEqual(plan.redirect_section, ProfileSectionId.EVIDENCE)
        self.assertTrue(plan.refresh_summary)
        self.assertTrue(plan.refresh_signals)
        self.assertFalse(plan.refresh_cv_preview)


if __name__ == "__main__":
    unittest.main()
