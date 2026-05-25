"""Presentation helpers for conservative application follow-up signals."""

from __future__ import annotations

from datetime import date, datetime

TERMINAL_STATES = {"Done", "Rejected"}
AGE_SIGNAL_RULES = {
    "Pending": (7, "Lleva tiempo pendiente"),
    "Applied": (21, "Lleva tiempo aplicada"),
    "Technical Test": (14, "Lleva tiempo en prueba tecnica"),
    "In Interview": (14, "Lleva tiempo en entrevista"),
    "Open Offer": (14, "Lleva tiempo en oferta"),
}


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _reference_date(application: dict) -> date | None:
    return _as_date(application.get("fecha_aplicacion")) or _as_date(application.get("fecha_registro"))


def _age_days(application: dict, *, today: date) -> int | None:
    reference_date = _reference_date(application)
    if reference_date is None:
        return None
    return max((today - reference_date).days, 0)


def _has_notes(application: dict) -> bool:
    return bool((application.get("notas") or "").strip())


def _has_contact(application: dict) -> bool:
    return any(
        (application.get(field) or "").strip()
        for field in ("nombre_recruiter", "email_recruiter", "telefono_recruiter")
    )


def build_follow_up_signals(application: dict, *, today: date | None = None) -> list[dict]:
    current_status = application.get("estado")
    today_value = today or date.today()

    if current_status in TERMINAL_STATES:
        return [
            {
                "kind": "terminal",
                "label": "Terminal",
                "tone": "gray",
                "compact": False,
            }
        ]

    signals: list[dict] = []
    age_days = _age_days(application, today=today_value)
    age_rule = AGE_SIGNAL_RULES.get(current_status)
    if age_rule and age_days is not None and age_days >= age_rule[0]:
        signals.append(
            {
                "kind": "age",
                "label": age_rule[1],
                "tone": "amber",
                "compact": True,
            }
        )

    if current_status == "Pending":
        signals.append(
            {
                "kind": "status",
                "label": "Pendiente por aplicar",
                "tone": "blue",
                "compact": True,
            }
        )

    if not _has_notes(application):
        signals.append(
            {
                "kind": "missing",
                "label": "Sin notas",
                "tone": "gray",
                "compact": True,
            }
        )

    if not _has_contact(application):
        signals.append(
            {
                "kind": "missing",
                "label": "Sin contacto",
                "tone": "gray",
                "compact": True,
            }
        )

    return signals


def pick_compact_follow_up_signal(signals: list[dict]) -> dict | None:
    return next((signal for signal in signals if signal.get("compact")), None)


__all__ = [
    "TERMINAL_STATES",
    "build_follow_up_signals",
    "pick_compact_follow_up_signal",
]
