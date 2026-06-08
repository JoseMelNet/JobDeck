"""Presentation helpers for the Credentials section of Perfil Laboral."""

from __future__ import annotations

from dataclasses import dataclass


def _has_text(value) -> bool:
    return bool(value and str(value).strip())


@dataclass(frozen=True)
class ProfileCredentialCategorySummary:
    total: int
    with_issuer_count: int
    with_url_count: int
    incomplete_count: int


@dataclass(frozen=True)
class ProfileCredentialsInventory:
    total_credentials: int
    education: ProfileCredentialCategorySummary
    courses: ProfileCredentialCategorySummary
    certifications: ProfileCredentialCategorySummary
    with_issuer_total: int
    with_url_total: int
    incomplete_total: int
    alerts: tuple[str, ...]
    summary: str
    is_empty: bool


def _build_education_summary(education: list[dict]) -> ProfileCredentialCategorySummary:
    return ProfileCredentialCategorySummary(
        total=len(education),
        with_issuer_count=sum(1 for item in education if _has_text(item.get("institucion"))),
        with_url_count=0,
        incomplete_count=sum(
            1
            for item in education
            if not _has_text(item.get("titulo"))
            or not _has_text(item.get("institucion"))
            or not _has_text(item.get("nivel"))
        ),
    )


def _build_course_summary(courses: list[dict]) -> ProfileCredentialCategorySummary:
    return ProfileCredentialCategorySummary(
        total=len(courses),
        with_issuer_count=sum(1 for item in courses if _has_text(item.get("institucion"))),
        with_url_count=sum(1 for item in courses if _has_text(item.get("url_certificado"))),
        incomplete_count=sum(
            1
            for item in courses
            if not _has_text(item.get("titulo"))
            or not _has_text(item.get("institucion"))
        ),
    )


def _build_certification_summary(certifications: list[dict]) -> ProfileCredentialCategorySummary:
    return ProfileCredentialCategorySummary(
        total=len(certifications),
        with_issuer_count=sum(1 for item in certifications if _has_text(item.get("institucion"))),
        with_url_count=sum(1 for item in certifications if _has_text(item.get("url_certificado"))),
        incomplete_count=sum(
            1
            for item in certifications
            if not _has_text(item.get("titulo"))
            or not _has_text(item.get("institucion"))
        ),
    )


def build_profile_credentials_inventory(
    education: list[dict],
    courses: list[dict],
    certifications: list[dict],
) -> ProfileCredentialsInventory:
    education_summary = _build_education_summary(education)
    course_summary = _build_course_summary(courses)
    certification_summary = _build_certification_summary(certifications)

    total_credentials = education_summary.total + course_summary.total + certification_summary.total
    with_issuer_total = (
        education_summary.with_issuer_count
        + course_summary.with_issuer_count
        + certification_summary.with_issuer_count
    )
    with_url_total = course_summary.with_url_count + certification_summary.with_url_count
    incomplete_total = (
        education_summary.incomplete_count
        + course_summary.incomplete_count
        + certification_summary.incomplete_count
    )

    is_empty = total_credentials == 0
    alerts: list[str] = []

    if is_empty:
        alerts.append("Aun no hay credenciales registradas para respaldar el perfil.")
    if incomplete_total:
        alerts.append(f"Hay {incomplete_total} credencial(es) con datos base incompletos.")
    if total_credentials and with_issuer_total < total_credentials:
        alerts.append("Algunas credenciales aun no muestran institucion o emisor claros.")
    if (course_summary.total + certification_summary.total) and with_url_total == 0:
        alerts.append("Cursos y certificaciones aun no tienen URLs verificables registradas.")
    elif (course_summary.total + certification_summary.total) > with_url_total:
        alerts.append("Parte de los cursos o certificaciones sigue sin URL o soporte verificable.")

    if is_empty:
        summary = "Todavia no existe soporte profesional registrado en esta seccion."
    else:
        summary = (
            f"{education_summary.total} educacion, {course_summary.total} curso(s) y "
            f"{certification_summary.total} certificacion(es) respaldan hoy el perfil."
        )

    return ProfileCredentialsInventory(
        total_credentials=total_credentials,
        education=education_summary,
        courses=course_summary,
        certifications=certification_summary,
        with_issuer_total=with_issuer_total,
        with_url_total=with_url_total,
        incomplete_total=incomplete_total,
        alerts=tuple(alerts[:4]),
        summary=summary,
        is_empty=is_empty,
    )


__all__ = [
    "ProfileCredentialCategorySummary",
    "ProfileCredentialsInventory",
    "build_profile_credentials_inventory",
]
