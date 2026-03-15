"""
database.py - CRUD para tabla de vacantes
VERSIÓN CON LINK: Incluye campo link en inserción
"""
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Optional, Dict

# Cargar variables de entorno
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost\\MSSQLSERVER2025")
DB_DATABASE = os.getenv("DB_DATABASE", "job_postings_mvp")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Micontraseña")

# Detectar qué ODBC Driver usar
AVAILABLE_DRIVERS = pyodbc.drivers()


def get_odbc_driver():
    """Detecta qué ODBC Driver está disponible"""
    for driver in AVAILABLE_DRIVERS:
        if "ODBC Driver 17 for SQL Server" in driver:
            return "ODBC Driver 17 for SQL Server"
    for driver in AVAILABLE_DRIVERS:
        if "ODBC Driver 11 for SQL Server" in driver:
            return "ODBC Driver 11 for SQL Server"
    return "ODBC Driver for SQL Server"


ODBC_DRIVER = get_odbc_driver()

print(f"[INFO] Usando ODBC Driver: {ODBC_DRIVER}")

# Connection string
CONNECTION_STRING = (
    f"Driver={{{ODBC_DRIVER}}};"
    f"Server={DB_SERVER};"
    f"Database={DB_DATABASE};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
)


def get_connection():
    """Establece conexión a SQL Server"""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except pyodbc.Error as e:
        print(f"[ERROR] Error de conexión: {e}")
        return None


def test_connection() -> bool:
    """Test rápido de conexión a BD"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except:
            pass
        finally:
            conn.close()
        return True
    return False


def insertar_vacante(empresa: str, cargo: str, modalidad: str, descripcion: str, link: Optional[str] = None) -> Dict:
    """
    Inserta una nueva vacante en la BD
    Retorna dict con: {'success': bool, 'message': str, 'id': int}

    Parámetros:
    - empresa: Nombre de la empresa
    - cargo: Posición laboral
    - modalidad: Remoto/Presencial/Híbrido
    - descripcion: Descripción de la vacante
    - link: (Opcional) URL de la vacante
    """
    conn = get_connection()
    if not conn:
        return {
            'success': False,
            'message': 'Error: No hay conexión a la base de datos',
            'id': None
        }

    try:
        cursor = conn.cursor()

        # Validar que modalidad sea válida
        modalidades_validas = ['Remoto', 'Presencial', 'Híbrido']
        if modalidad not in modalidades_validas:
            return {
                'success': False,
                'message': f'Modalidad inválida. Usa: {", ".join(modalidades_validas)}',
                'id': None
            }

        # INSERTAR CON LINK
        query = """
        INSERT INTO vacantes (empresa, cargo, modalidad, link, descripcion)
        VALUES (?, ?, ?, ?, ?);
        """

        # Si link es None o vacío, pasar NULL a la BD
        link_value = link if link and link.strip() else None

        cursor.execute(query, (empresa, cargo, modalidad, link_value, descripcion))

        # Obtener el ID usando @@IDENTITY
        cursor.execute("SELECT @@IDENTITY AS id;")
        result = cursor.fetchone()

        if result and result[0] is not None:
            vacante_id = int(result[0])
            conn.commit()

            print(f"[DEBUG] Vacante insertada con ID: {vacante_id}")

            cursor.close()
            conn.close()

            return {
                'success': True,
                'message': f'✓ Vacante guardada exitosamente (ID: {vacante_id})',
                'id': vacante_id
            }
        else:
            conn.rollback()
            cursor.close()
            conn.close()

            return {
                'success': False,
                'message': 'Error: No se pudo obtener el ID de la vacante',
                'id': None
            }

    except pyodbc.Error as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] pyodbc error: {e}")

        return {
            'success': False,
            'message': f'Error en BD: {str(e)}',
            'id': None
        }

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] Error inesperado: {e}")

        return {
            'success': False,
            'message': f'Error inesperado: {str(e)}',
            'id': None
        }

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


def obtener_todas_vacantes() -> List[Dict]:
    """
    Obtiene todas las vacantes ordenadas por fecha (más recientes primero)
    Retorna lista de dicts
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()

        query = """
        SELECT id, empresa, cargo, modalidad, link, descripcion, fecha_registro
        FROM vacantes
        ORDER BY fecha_registro DESC
        """
        cursor.execute(query)

        vacantes = []
        for row in cursor.fetchall():
            vacantes.append({
                'id': row[0],
                'empresa': row[1],
                'cargo': row[2],
                'modalidad': row[3],
                'link': row[4],
                'descripcion': row[5],
                'fecha_registro': row[6]
            })

        cursor.close()
        conn.close()
        return vacantes

    except pyodbc.Error as e:
        print(f"[ERROR] Error al obtener vacantes: {e}")
        return []

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return []

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


def obtener_vacante_por_id(vacante_id: int) -> Optional[Dict]:
    """Obtiene una vacante específica por ID"""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        query = """
        SELECT id, empresa, cargo, modalidad, link, descripcion, fecha_registro
        FROM vacantes
        WHERE id = ?
        """
        cursor.execute(query, (vacante_id,))
        row = cursor.fetchone()

        if row:
            result = {
                'id': row[0],
                'empresa': row[1],
                'cargo': row[2],
                'modalidad': row[3],
                'link': row[4],
                'descripcion': row[5],
                'fecha_registro': row[6]
            }
            cursor.close()
            conn.close()
            return result

        cursor.close()
        conn.close()
        return None

    except pyodbc.Error as e:
        print(f"[ERROR] Error al obtener vacante: {e}")
        return None

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return None

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


def eliminar_vacante(vacante_id: int) -> Dict:
    """Elimina una vacante por ID"""
    conn = get_connection()
    if not conn:
        return {
            'success': False,
            'message': 'Error: No hay conexión a la base de datos'
        }

    try:
        cursor = conn.cursor()

        query = "DELETE FROM vacantes WHERE id = ?"
        cursor.execute(query, (vacante_id,))
        conn.commit()

        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return {
                'success': True,
                'message': f'✓ Vacante ID {vacante_id} eliminada'
            }
        else:
            cursor.close()
            conn.close()
            return {
                'success': False,
                'message': f'No se encontró vacante con ID {vacante_id}'
            }

    except pyodbc.Error as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] Error al eliminar: {e}")

        return {
            'success': False,
            'message': f'Error en BD: {str(e)}'
        }

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] Error inesperado: {e}")

        return {
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        }

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


def contar_vacantes() -> int:
    """Retorna el total de vacantes registradas"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vacantes")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count

    except pyodbc.Error as e:
        print(f"[ERROR] Error al contar: {e}")
        return 0

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return 0

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass


# Debug: Mostrar configuración
if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURACIÓN DE CONEXIÓN")
    print("=" * 60)
    print(f"Servidor: {DB_SERVER}")
    print(f"Base de Datos: {DB_DATABASE}")
    print(f"Usuario: {DB_USER}")
    print(f"ODBC Driver: {ODBC_DRIVER}")
    print("=" * 60)

    if test_connection():
        print("✅ Conexión exitosa")
    else:
        print("❌ Error de conexión")