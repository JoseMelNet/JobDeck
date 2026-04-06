"""Quick SQL Server connectivity smoke test."""

from __future__ import annotations

import sys

import pyodbc

from app.infrastructure.persistence.connection import build_connection_string, test_connection
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository

vacancy_repository = VacancyRepository()
connection_string = build_connection_string()

print("=" * 60)
print("TEST DE CONEXION A SQL SERVER")
print("=" * 60)

print("\n[1/4] Probando conexion a SQL Server...")
if test_connection():
    print("Conexion exitosa")
else:
    print("Error de conexion")
    print(f"\nString de conexion: {connection_string}")
    sys.exit(1)

print("\n[2/4] Contando vacantes...")
try:
    total = vacancy_repository.count()
    print(f"Total de vacantes: {total}")
except Exception as exc:
    print(f"Error: {exc}")
    sys.exit(1)

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
    sys.exit(1)

print("\n[4/4] Validando estructura de BD...")
try:
    conn = pyodbc.connect(connection_string)
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
        sys.exit(1)
    cursor.close()
    conn.close()
except Exception as exc:
    print(f"Error: {exc}")
    sys.exit(1)

print("\n" + "=" * 60)
print("TODOS LOS TESTS PASARON")
print("=" * 60)
print("\nYa puedes ejecutar la interfaz principal con: uvicorn api:app --reload\n")
