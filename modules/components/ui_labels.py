"""Shared UI labels and catalog metadata for management screens."""

from __future__ import annotations

VACANCY_SEMAPHORE_META = {
    "verde": {"emoji": "green", "label": "Alta afinidad", "color": "#10B981"},
    "amarillo": {"emoji": "yellow", "label": "Afinidad media", "color": "#F59E0B"},
    "rojo": {"emoji": "red", "label": "Baja afinidad", "color": "#EF4444"},
    "gris": {"emoji": "white", "label": "Sin analizar", "color": "#9CA3AF"},
}

APPLICATION_STATUS_META = {
    "Pending": {"emoji": "pending", "color": "#6B7280", "bg": "#F3F4F6"},
    "Applied": {"emoji": "applied", "color": "#3B82F6", "bg": "#EFF6FF"},
    "Technical Test": {"emoji": "test", "color": "#A855F7", "bg": "#FAF5FF"},
    "In Interview": {"emoji": "interview", "color": "#F59E0B", "bg": "#FFFBEB"},
    "Done": {"emoji": "done", "color": "#10B981", "bg": "#ECFDF5"},
    "Rejected": {"emoji": "rejected", "color": "#EF4444", "bg": "#FFF1F2"},
    "Open Offer": {"emoji": "offer", "color": "#EC4899", "bg": "#FDF4FF"},
}

APPLICATION_MODALITY_META = {
    "Remoto": {"emoji": "remoto", "color": "#3B82F6"},
    "Presencial": {"emoji": "presencial", "color": "#EF4444"},
    "Hibrido": {"emoji": "hibrido", "color": "#A855F7"},
}

VACANCY_FILTER_STATES = ["Activas", "Archivadas", "Todas"]
VACANCY_MODALITY_OPTIONS = ["Remoto", "Presencial", "Hibrido"]


def normalize_modality_label(value: str | None) -> str:
    if not value:
        return "-"

    normalized = (
        value.strip()
        .replace("H\u00edbrido", "Hibrido")
        .replace("H\u00c3\u00adbrido", "Hibrido")
    )
    if normalized in ("Remoto", "Presencial", "Hibrido"):
        return normalized
    return normalized
