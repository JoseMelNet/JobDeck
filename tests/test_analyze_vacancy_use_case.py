"""Tests for AnalyzeVacancyUseCase."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.domain.exceptions import AnalysisError


class AnalyzeVacancyUseCaseTests(unittest.TestCase):
    def test_raises_error_when_vacancy_does_not_exist(self):
        vacancy_repository = Mock()
        vacancy_repository.get_by_id.return_value = None
        profile_repository = Mock()
        analysis_repository = Mock()
        use_case = AnalyzeVacancyUseCase(vacancy_repository, profile_repository, analysis_repository)

        with self.assertRaises(AnalysisError):
            use_case.execute(1)

    def test_skips_analysis_when_profile_does_not_exist(self):
        vacancy_repository = Mock()
        vacancy_repository.get_by_id.return_value = {"id": 1}
        profile_repository = Mock()
        profile_repository.get_active_profile.return_value = None
        analysis_repository = Mock()
        use_case = AnalyzeVacancyUseCase(vacancy_repository, profile_repository, analysis_repository)

        result = use_case.execute(1)

        self.assertTrue(result["success"])
        self.assertFalse(result["analizado"])
        self.assertTrue(result["omitido"])

    @patch("app.application.use_cases.analyze_vacancy.analizar_vacante")
    def test_executes_full_analysis_flow(self, analizar_vacante_mock):
        vacancy_repository = Mock()
        vacancy_repository.get_by_id.return_value = {"id": 1, "cargo": "Data Analyst"}
        profile_repository = Mock()
        profile_repository.get_active_profile.return_value = {"id": 2}
        analysis_repository = Mock()
        analysis_repository.save.return_value = {"success": True, "message": "Saved"}
        use_case = AnalyzeVacancyUseCase(vacancy_repository, profile_repository, analysis_repository)
        use_case.analysis_service = Mock()
        use_case.analysis_service.build_profile_payload.return_value = {"nombre": "Ana"}
        analizar_vacante_mock.return_value = {"success": True, "score_total": 80}

        result = use_case.execute(1)

        self.assertTrue(result["success"])
        self.assertTrue(result["analizado"])
        self.assertFalse(result["omitido"])
        analysis_repository.save.assert_called_once_with(1, 2, {"success": True, "score_total": 80})

    @patch("app.application.use_cases.analyze_vacancy.analizar_vacante")
    def test_raises_error_when_analysis_fails(self, analizar_vacante_mock):
        vacancy_repository = Mock()
        vacancy_repository.get_by_id.return_value = {"id": 1}
        profile_repository = Mock()
        profile_repository.get_active_profile.return_value = {"id": 2}
        analysis_repository = Mock()
        use_case = AnalyzeVacancyUseCase(vacancy_repository, profile_repository, analysis_repository)
        use_case.analysis_service = Mock()
        use_case.analysis_service.build_profile_payload.return_value = {"nombre": "Ana"}
        analizar_vacante_mock.return_value = {"success": False, "message": "boom"}

        with self.assertRaises(AnalysisError):
            use_case.execute(1)


if __name__ == "__main__":
    unittest.main()
