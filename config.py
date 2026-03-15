"""
config.py - Configuración de conexión a SQL Server MSSQLSERVER2025
ACTUALIZADO PARA: ODBC Driver 17 + MSSQLSERVER2025
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración SQL Server
# IMPORTANTE: Cambia DB_SERVER a tu instancia correcta
DB_SERVER = os.getenv("DB_SERVER", "localhost\\MSSQLSERVER2025")  # ← ACTUALIZADO
DB_DATABASE = os.getenv("DB_DATABASE", "job_postings_mvp")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Micontraseña")  # ← ACTUALIZADO

# Connection string para pyodbc - ODBC Driver 17
# ¡IMPORTANTE! Especificar explícitamente Driver 17
CONNECTION_STRING = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"  # ← DRIVER 17 REQUERIDO
    f"Server={DB_SERVER};"
    f"Database={DB_DATABASE};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    f"TrustServerCertificate=yes;"  # ← Agregado para evitar problemas SSL
)

# Opciones de modalidad
MODALIDADES = ["Remoto", "Presencial", "Híbrido"]

# Debug: Mostrar conexión (comentar en producción)
if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURACIÓN DE CONEXIÓN")
    print("=" * 60)
    print(f"Servidor: {DB_SERVER}")
    print(f"Base de Datos: {DB_DATABASE}")
    print(f"Usuario: {DB_USER}")
    print(f"Contraseña: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(vacía)'}")
    print(f"Driver: ODBC Driver 17 for SQL Server")
    print("=" * 60)