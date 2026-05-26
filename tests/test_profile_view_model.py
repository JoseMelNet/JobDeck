"""Tests for the Perfil Laboral presentation contract."""

from __future__ import annotations

import unittest

from app.interfaces.web.presentation.profile_view_model import (
    ProfileDataConsumer,
    ProfileFieldPriority,
    ProfileFieldUsage,
    ProfileSectionId,
    build_profile_labor_contract,
)


class ProfileViewModelContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = build_profile_labor_contract()

    def test_sections_follow_target_navigation_order(self):
        self.assertEqual(
            [section.id for section in self.contract.sections],
            [
                ProfileSectionId.SUMMARY,
                ProfileSectionId.OBJECTIVE,
                ProfileSectionId.SIGNALS,
                ProfileSectionId.EVIDENCE,
                ProfileSectionId.CREDENTIALS,
                ProfileSectionId.OUTPUTS,
            ],
        )

    def test_basics_block_is_explicitly_split_between_objective_and_outputs(self):
        basics_block = next(block for block in self.contract.blocks if block.current_block_id == "basics")

        self.assertEqual(
            basics_block.target_sections,
            (ProfileSectionId.OBJECTIVE, ProfileSectionId.OUTPUTS),
        )

    def test_project_fields_are_evidence_and_not_current_analysis_inputs(self):
        stack_field = self.contract.field_by_key("projects", "stack")

        self.assertEqual(stack_field.target_section, ProfileSectionId.EVIDENCE)
        self.assertNotIn(ProfileFieldUsage.VACANCY_ANALYSIS, stack_field.target_usages)
        self.assertEqual(stack_field.current_consumers, (ProfileDataConsumer.PROFILE_UI,))

    def test_contact_fields_are_output_focused_and_address_is_secondary(self):
        address_field = self.contract.field_by_key("basics", "direccion")
        email_field = self.contract.field_by_key("basics", "correo")

        self.assertEqual(address_field.target_section, ProfileSectionId.OUTPUTS)
        self.assertEqual(address_field.priority, ProfileFieldPriority.SECONDARY)
        self.assertIn(ProfileFieldUsage.OUTPUT_CONTACT, email_field.target_usages)

    def test_analysis_usage_collects_skills_and_experience(self):
        analysis_fields = self.contract.fields_for_usage(ProfileFieldUsage.VACANCY_ANALYSIS)
        analysis_keys = {(field.current_block_id, field.field_id) for field in analysis_fields}

        self.assertIn(("skills", "skill"), analysis_keys)
        self.assertIn(("experiences", "logros"), analysis_keys)
        self.assertNotIn(("projects", "stack"), analysis_keys)


if __name__ == "__main__":
    unittest.main()
