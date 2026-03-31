"""Tests for RegisterApplicationUseCase."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from app.application.use_cases.register_application import RegisterApplicationUseCase
from app.domain.exceptions import ValidationError


class RegisterApplicationUseCaseTests(unittest.TestCase):
    def test_raises_validation_error_for_invalid_status(self):
        repository = Mock()
        use_case = RegisterApplicationUseCase(repository)

        with self.assertRaises(ValidationError):
            use_case.execute(estado="Unknown", empresa="ACME")

        repository.create.assert_not_called()

    def test_normalizes_status_and_delegates_to_repository(self):
        repository = Mock()
        repository.create.return_value = {"success": True, "id": 9}
        use_case = RegisterApplicationUseCase(repository)

        result = use_case.execute(
            estado=" Applied ",
            empresa="ACME",
            cargo="Data Analyst",
        )

        self.assertEqual(result, {"success": True, "id": 9})
        repository.create.assert_called_once_with(
            estado="Applied",
            empresa="ACME",
            cargo="Data Analyst",
        )


if __name__ == "__main__":
    unittest.main()
