"""Shared decision presentation helpers for vacancy analysis."""

from __future__ import annotations

import unicodedata

DECISION_TONE_MAP = {
    "apply_strong": "green",
    "apply_later": "amber",
    "discard": "red",
    "unknown": "gray",
}

COHERENCE_LABELS = {
    "aligned": "Coherente",
    "cautious_high_score": "Score alto con decision cauta",
    "cautious_discard": "Score competitivo con descarte",
    "optimistic_low_score": "Decision optimista con score bajo",
    "missing_score": "Decision sin score",
    "missing_decision": "Score sin decision",
    "unknown_decision": "Decision desconocida",
}


def _safe_score(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""

    collapsed = " ".join(str(value).strip().split())
    normalized = unicodedata.normalize("NFKD", collapsed)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _score_band(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _score_tone(score_band: str) -> str:
    return {
        "high": "green",
        "medium": "amber",
        "low": "red",
        "unknown": "gray",
    }.get(score_band, "gray")


def _normalize_decision(decision: str | None) -> tuple[str | None, str]:
    cleaned = str(decision).strip() if decision is not None else ""
    if not cleaned or cleaned.lower() in {"null", "none", "n/a", "na", "-"}:
        return None, "unknown"

    normalized = _normalize_text(cleaned)
    if "aplicar si sobra tiempo" in normalized:
        return cleaned, "apply_later"
    if "aplicar si o si" in normalized:
        return cleaned, "apply_strong"
    if any(keyword in normalized for keyword in ("no aplicar", "descartar", "rechazar")):
        return cleaned, "discard"
    if any(keyword in normalized for keyword in ("revis", "evalu", "consider")):
        return cleaned, "apply_later"
    if any(keyword in normalized for keyword in ("aplicar", "prior", "avanz")):
        return cleaned, "apply_strong"
    return cleaned, "unknown"


def _coherence_status(score_band: str, decision_normalized: str, *, has_decision: bool) -> str:
    if not has_decision and score_band != "unknown":
        return "missing_decision"
    if has_decision and score_band == "unknown":
        return "missing_score"
    if decision_normalized == "unknown":
        return "unknown_decision"
    if decision_normalized == "apply_later" and score_band == "high":
        return "cautious_high_score"
    if decision_normalized == "discard" and score_band in {"high", "medium"}:
        return "cautious_discard"
    if decision_normalized == "apply_strong" and score_band == "low":
        return "optimistic_low_score"
    return "aligned"


def _build_decision_signal(analysis: dict | None) -> dict:
    score = _safe_score(analysis.get("score_total")) if analysis else None
    score_value = round(score) if score is not None else None
    score_band = _score_band(score)
    score_tone = _score_tone(score_band)
    score_label = f"{score_value:.0f}" if score_value is not None else "-"
    decision_raw, decision_normalized = _normalize_decision(
        analysis.get("decision_aplicacion") if analysis else None
    )

    if decision_normalized == "apply_strong":
        decision_label = decision_raw or "Aplicar si o si"
        decision_compact_label = "Si"
    elif decision_normalized == "apply_later":
        decision_label = decision_raw or "Aplicar si sobra tiempo"
        decision_compact_label = "Si hay tiempo"
    elif decision_normalized == "discard":
        decision_label = decision_raw or "Descartar"
        decision_compact_label = "No"
    else:
        if decision_raw:
            decision_label = decision_raw
            decision_compact_label = "Sin decision"
        else:
            decision_label = "Pendiente de analisis" if not analysis else "Sin decision"
            decision_compact_label = "Pendiente"

    decision_tone = DECISION_TONE_MAP[decision_normalized]
    coherence_status = _coherence_status(
        score_band,
        decision_normalized,
        has_decision=bool(decision_raw),
    )
    score_title = f"Score {score_label}" if score_value is not None else "Score pendiente"
    title_parts = [decision_label]
    if score_value is not None:
        title_parts.append(f"Score {score_label}")

    return {
        "score": score_value,
        "score_label": score_label,
        "score_band": score_band,
        "score_tone": score_tone,
        "decision_raw": decision_raw,
        "decision_normalized": decision_normalized,
        "decision_label": decision_label,
        "decision_compact_label": decision_compact_label,
        "decision_tone": decision_tone,
        "display_tone": decision_tone,
        "coherence_status": coherence_status,
        "coherence_label": COHERENCE_LABELS[coherence_status],
        "title": " · ".join(title_parts),
        "aria_label": " · ".join(title_parts),
        "score_title": score_title,
    }


__all__ = [
    "COHERENCE_LABELS",
    "DECISION_TONE_MAP",
    "_build_decision_signal",
    "_coherence_status",
    "_normalize_decision",
    "_normalize_text",
    "_safe_score",
    "_score_band",
    "_score_tone",
]
