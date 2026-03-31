"""Integration-style tests for core business flows using mocks."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.application.use_cases.register_application import RegisterApplicationUseCase


class IntegrationFlowTests(unittest.TestCase):
    @patch("app.application.use_cases.analyze_vacancy.analizar_vacante")
    def test_create_analyze_and_register_application_flow(self, analizar_vacante_mock):
        vacancy_repository = Mock()
        vacancy_repository.create.return_value = {"success": True, "message": "saved", "id": 12}
        vacancy_repository.get_by_id.return_value = {"id": 12, "empresa": "ACME", "cargo": "Data Analyst"}

        profile_repository = Mock()
        profile_repository.get_active_profile.return_value = {"id": 3}

        analysis_repository = Mock()
        analysis_repository.save.return_value = {"success": True, "message": "analysis saved"}

        application_repository = Mock()
        application_repository.create.return_value = {"success": True, "message": "application saved", "id": 99}

        create_use_case = CreateVacancyUseCase(vacancy_repository)
        analyze_use_case = AnalyzeVacancyUseCase(vacancy_repository, profile_repository, analysis_repository)
        analyze_use_case.analysis_service = Mock()
        analyze_use_case.analysis_service.build_profile_payload.return_value = {"nombre": "Ana"}
        register_use_case = RegisterApplicationUseCase(application_repository)

        analizar_vacante_mock.return_value = {"success": True, "score_total": 80}

        created = create_use_case.execute(
            empresa="ACME",
            cargo="Data Analyst",
            modalidad="Remoto",
            descripcion="Desc",
        )
        analyzed = analyze_use_case.execute(created["id"])
        registered = register_use_case.execute(
            vacante_id=created["id"],
            estado="Applied",
            fecha_aplicacion="2026-03-30",
        )

        self.assertTrue(created["success"])
        self.assertTrue(analyzed["analizado"])
        self.assertTrue(registered["success"])
        analysis_repository.save.assert_called_once()
        application_repository.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
