"""Database connectivity helpers.

This module mirrors the current legacy connection behavior so the migration can
move incrementally without changing runtime behavior.
"""

from __future__ import annotations

import pyodbc

from app.config.settings import settings


def get_odbc_driver() -> str:
    """Return the preferred SQL Server ODBC driver available in the machine."""
    available_drivers = pyodbc.drivers()
    for driver in available_drivers:
        if "ODBC Driver 17 for SQL Server" in driver:
            return "ODBC Driver 17 for SQL Server"
    for driver in available_drivers:
        if "ODBC Driver 11 for SQL Server" in driver:
            return "ODBC Driver 11 for SQL Server"
    return "ODBC Driver for SQL Server"


def build_connection_string() -> str:
    driver = get_odbc_driver()
    return (
        f"Driver={{{driver}}};"
        f"Server={settings.db_server};"
        f"Database={settings.db_database};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
    )


def get_connection():
    """Create a pyodbc connection using centralized settings."""
    return pyodbc.connect(build_connection_string())


def test_connection() -> bool:
    """Run a lightweight database connectivity check."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return True
    except pyodbc.Error:
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
