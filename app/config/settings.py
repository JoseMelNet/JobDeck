"""Centralized settings for the application."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _optional_env(key: str) -> str | None:
    value = os.getenv(key)
    if value is None:
        return None
    value = value.strip()
    return value or None


@dataclass(frozen=True)
class Settings:
    db_server: str = os.getenv("DB_SERVER", "localhost\\MSSQLSERVER2025")
    db_database: str = os.getenv("DB_DATABASE", "job_postings_mvp")
    db_user: str | None = _optional_env("DB_USER")
    db_password: str | None = _optional_env("DB_PASSWORD")


settings = Settings()
