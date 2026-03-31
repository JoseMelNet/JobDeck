"""Use case for registering job applications."""

from __future__ import annotations

from app.domain.enums.application_status import APPLICATION_STATUSES
from app.domain.exceptions import ValidationError
from app.infrastructure.persistence.repositories.application_repository import ApplicationRepository


class RegisterApplicationUseCase:
    """Register an application with domain-level status validation."""

    def __init__(self, application_repository: ApplicationRepository) -> None:
        self.application_repository = application_repository

    def execute(self, **payload) -> dict:
        estado = payload.get("estado", "").strip()
        if estado not in APPLICATION_STATUSES:
            raise ValidationError(f"Estado inválido: {estado}")

        payload["estado"] = estado
        return self.application_repository.create(**payload)
