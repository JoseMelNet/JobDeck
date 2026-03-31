"""Tests for CreateVacancyUseCase."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.domain.exceptions import ValidationError


class CreateVacancyUseCaseTests(unittest.TestCase):
    def test_raises_validation_error_for_invalid_modality(self):
        repository = Mock()
        use_case = CreateVacancyUseCase(repository)

        with self.assertRaises(ValidationError):
            use_case.execute(
                empresa="ACME",
                cargo="Data Analyst",
                modalidad="Invalid",
                descripcion="Desc",
            )

        repository.create.assert_not_called()

    def test_strips_fields_and_calls_repository(self):
        repository = Mock(return_value=None)
        repository.create.return_value = {"success": True, "id": 1}
        use_case = CreateVacancyUseCase(repository)

        result = use_case.execute(
            empresa=" ACME ",
            cargo=" Data Analyst ",
            modalidad="Remoto",
            descripcion=" Desc ",
            link="https://example.com",
        )

        self.assertEqual(result, {"success": True, "id": 1})
        repository.create.assert_called_once_with(
            empresa="ACME",
            cargo="Data Analyst",
            modalidad="Remoto",
            descripcion="Desc",
            link="https://example.com",
        )


if __name__ == "__main__":
    unittest.main()
