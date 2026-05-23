"""Quick SQL Server connectivity smoke test."""

from __future__ import annotations

import pyodbc

from app.infrastructure.persistence.connection import (
    DatabaseConfigurationError,
    build_safe_connection_summary,
    get_connection,
    test_connection,
    validate_database_settings,
)
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository

def main() -> int:
    vacancy_repository = VacancyRepository()

    print("=" * 60)
    print("TEST DE CONEXION A SQL SERVER")
    print("=" * 60)

    print("\n[1/4] Probando conexion a SQL Server...")
    try:
        validate_database_settings()
    except DatabaseConfigurationError as exc:
        print(f"Configuracion incompleta: {exc}")
        print(f"\nResumen seguro de configuracion: {build_safe_connection_summary()}")
        return 1

    if test_connection():
        print("Conexion exitosa")
    else:
        print("Error de conexion")
        print(f"\nResumen seguro de configuracion: {build_safe_connection_summary()}")
        return 1

    print("\n[2/4] Contando vacantes...")
    try:
        total = vacancy_repository.count()
        print(f"Total de vacantes: {total}")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print("\n[3/4] Obteniendo todas las vacantes...")
    try:
        vacantes = vacancy_repository.list_all()
        if vacantes:
            print(f"Se obtuvieron {len(vacantes)} vacante(s)")
            for vacante in vacantes[:2]:
                print(f"   - {vacante['empresa']} | {vacante['cargo']}")
        else:
            print("Base de datos vacia (normal si es primera vez)")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print("\n[4/4] Validando estructura de BD...")
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'vacantes'
            """
        )
        if cursor.fetchone():
            print("Tabla 'vacantes' existe y es accesible")
        else:
            print("Tabla 'vacantes' no encontrada")
            return 1
    except (DatabaseConfigurationError, pyodbc.Error) as exc:
        print(f"Error: {exc}")
        return 1
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\nYa puedes ejecutar la interfaz principal con: uvicorn api:app --reload --port 8001\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
