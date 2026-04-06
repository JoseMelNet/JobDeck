"""Use case for creating vacancies."""

from __future__ import annotations

from app.domain.enums.modality import MODALITIES, normalize_modality
from app.domain.exceptions import ValidationError
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository


class CreateVacancyUseCase:
    """Create a vacancy with minimal validation."""

    def __init__(self, vacancy_repository: VacancyRepository) -> None:
        self.vacancy_repository = vacancy_repository

    def execute(self, *, empresa: str, cargo: str, modalidad: str, descripcion: str, link: str | None = None) -> dict:
        modalidad_normalizada = normalize_modality(modalidad)
        if modalidad_normalizada not in MODALITIES:
            raise ValidationError(f"Modalidad inválida: {modalidad_normalizada}")

        return self.vacancy_repository.create(
            empresa=empresa.strip(),
            cargo=cargo.strip(),
            modalidad=modalidad_normalizada,
            descripcion=descripcion.strip(),
            link=link,
        )
