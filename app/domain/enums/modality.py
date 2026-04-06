"""Vacancy modality values."""

MODALITIES = ("Remoto", "Presencial", "Híbrido")


def normalize_modality(value: str) -> str:
    normalized = value.strip()
    aliases = {
        "remoto": "Remoto",
        "presencial": "Presencial",
        "hibrido": "Híbrido",
        "híbrido": "Híbrido",
    }
    return aliases.get(normalized.lower(), normalized)
