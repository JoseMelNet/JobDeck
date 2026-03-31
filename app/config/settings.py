"""Centralized settings for the application."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_server: str = os.getenv("DB_SERVER", "localhost\\MSSQLSERVER2025")
    db_database: str = os.getenv("DB_DATABASE", "job_postings_mvp")
    db_user: str = os.getenv("DB_USER", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "Micontraseña")


settings = Settings()
