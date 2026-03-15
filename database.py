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


"""
database_aplicaciones.py
Nuevas funciones CRUD para la tabla "aplicaciones".

INSTRUCCIONES: Copia estas funciones al final de tu database.py existente.
"""

# ============================================================
# FUNCIONES DE APLICACIONES
# Pega todo este bloque al final de database.py
# ============================================================

def insertar_aplicacion(
    vacante_id: int,
    fecha_aplicacion,
    estado: str,
    nombre_recruiter: str = None,
    email_recruiter: str = None,
    telefono_recruiter: str = None,
    notas: str = None
) -> dict:
    """
    Inserta una nueva aplicación en la BD.
    Valida que no exista una aplicación previa para la misma vacante.

    Retorna dict con: {'success': bool, 'message': str, 'id': int}
    """
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Error: No hay conexión a la base de datos', 'id': None}

    try:
        cursor = conn.cursor()

        # Validar estado
        estados_validos = ['Pending', 'Applied', 'Technical Test', 'In Interview', 'Done', 'Rejected', 'Open Offer']
        if estado not in estados_validos:
            return {'success': False, 'message': f'Estado inválido. Usa: {", ".join(estados_validos)}', 'id': None}

        # Verificar si ya existe aplicación para esta vacante
        cursor.execute("SELECT id FROM aplicaciones WHERE vacante_id = ?", (vacante_id,))
        if cursor.fetchone():
            return {
                'success': False,
                'message': '⚠️ Ya existe una aplicación registrada para esta vacante.',
                'id': None
            }

        # Limpiar campos opcionales
        def clean(val):
            return val.strip() if val and str(val).strip() else None

        cursor.execute("""
            INSERT INTO aplicaciones
                (vacante_id, fecha_aplicacion, estado, nombre_recruiter,
                 email_recruiter, telefono_recruiter, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            vacante_id,
            fecha_aplicacion,
            estado,
            clean(nombre_recruiter),
            clean(email_recruiter),
            clean(telefono_recruiter),
            clean(notas)
        ))

        cursor.execute("SELECT @@IDENTITY AS id;")
        result = cursor.fetchone()

        if result and result[0] is not None:
            aplicacion_id = int(result[0])
            conn.commit()
            cursor.close()
            conn.close()
            return {
                'success': True,
                'message': f'✓ Aplicación guardada exitosamente (ID: {aplicacion_id})',
                'id': aplicacion_id
            }
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            return {'success': False, 'message': 'Error: No se pudo obtener el ID de la aplicación', 'id': None}

    except pyodbc.Error as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] pyodbc insertar_aplicacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}', 'id': None}

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] insertar_aplicacion: {e}")
        return {'success': False, 'message': f'Error inesperado: {str(e)}', 'id': None}

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def obtener_todas_aplicaciones() -> list:
    """
    Obtiene todas las aplicaciones con datos de la vacante asociada.
    Ordenadas por fecha_aplicacion DESC.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id,
                a.vacante_id,
                v.empresa,
                v.cargo,
                v.modalidad,
                v.link,
                a.fecha_aplicacion,
                a.estado,
                a.nombre_recruiter,
                a.email_recruiter,
                a.telefono_recruiter,
                a.notas,
                a.fecha_registro
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.vacante_id = v.id
            ORDER BY a.fecha_aplicacion DESC
        """)

        aplicaciones = []
        for row in cursor.fetchall():
            aplicaciones.append({
                'id':                 row[0],
                'vacante_id':         row[1],
                'empresa':            row[2],
                'cargo':              row[3],
                'modalidad':          row[4],
                'link':               row[5],
                'fecha_aplicacion':   row[6],
                'estado':             row[7],
                'nombre_recruiter':   row[8],
                'email_recruiter':    row[9],
                'telefono_recruiter': row[10],
                'notas':              row[11],
                'fecha_registro':     row[12],
            })

        cursor.close()
        conn.close()
        return aplicaciones

    except Exception as e:
        print(f"[ERROR] obtener_todas_aplicaciones: {e}")
        return []

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def obtener_aplicacion_por_id(aplicacion_id: int) -> Optional[Dict]:
    """Obtiene una aplicación específica con datos de su vacante."""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id, a.vacante_id, v.empresa, v.cargo, v.modalidad, v.link,
                a.fecha_aplicacion, a.estado, a.nombre_recruiter,
                a.email_recruiter, a.telefono_recruiter, a.notas, a.fecha_registro
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.vacante_id = v.id
            WHERE a.id = ?
        """, (aplicacion_id,))

        row = cursor.fetchone()
        if row:
            return {
                'id': row[0], 'vacante_id': row[1], 'empresa': row[2],
                'cargo': row[3], 'modalidad': row[4], 'link': row[5],
                'fecha_aplicacion': row[6], 'estado': row[7],
                'nombre_recruiter': row[8], 'email_recruiter': row[9],
                'telefono_recruiter': row[10], 'notas': row[11],
                'fecha_registro': row[12],
            }
        return None

    except Exception as e:
        print(f"[ERROR] obtener_aplicacion_por_id: {e}")
        return None

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def actualizar_estado_aplicacion(aplicacion_id: int, nuevo_estado: str) -> Dict:
    """
    Actualiza solo el campo 'estado' de una aplicación.
    Estados válidos: Pending, Applied, Technical Test, In Interview, Done, Rejected, Open Offer
    """
    estados_validos = ['Pending', 'Applied', 'Technical Test', 'In Interview', 'Done', 'Rejected', 'Open Offer']
    if nuevo_estado not in estados_validos:
        return {'success': False, 'message': f'Estado inválido. Opciones: {", ".join(estados_validos)}'}

    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Error: No hay conexión a la base de datos'}

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE aplicaciones SET estado = ? WHERE id = ?",
            (nuevo_estado, aplicacion_id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return {'success': True, 'message': f'✓ Estado actualizado a "{nuevo_estado}"'}
        else:
            cursor.close()
            conn.close()
            return {'success': False, 'message': f'No se encontró aplicación con ID {aplicacion_id}'}

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] actualizar_estado_aplicacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def actualizar_datos_aplicacion(
    aplicacion_id: int,
    estado: str,
    nombre_recruiter: str = None,
    email_recruiter: str = None,
    telefono_recruiter: str = None,
    notas: str = None
) -> Dict:
    """
    Actualiza todos los campos editables de una aplicación (excepto vacante_id y fechas).
    """
    estados_validos = ['Pending', 'Applied', 'Technical Test', 'In Interview', 'Done', 'Rejected', 'Open Offer']
    if estado not in estados_validos:
        return {'success': False, 'message': f'Estado inválido. Opciones: {", ".join(estados_validos)}'}

    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Error: No hay conexión a la base de datos'}

    def clean(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE aplicaciones
            SET estado             = ?,
                nombre_recruiter   = ?,
                email_recruiter    = ?,
                telefono_recruiter = ?,
                notas              = ?
            WHERE id = ?
        """, (
            estado,
            clean(nombre_recruiter),
            clean(email_recruiter),
            clean(telefono_recruiter),
            clean(notas),
            aplicacion_id
        ))
        conn.commit()

        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return {'success': True, 'message': f'✓ Aplicación actualizada correctamente'}
        else:
            cursor.close()
            conn.close()
            return {'success': False, 'message': f'No se encontró aplicación con ID {aplicacion_id}'}

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] actualizar_datos_aplicacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def eliminar_aplicacion(aplicacion_id: int) -> Dict:
    """Elimina una aplicación por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Error: No hay conexión a la base de datos'}

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM aplicaciones WHERE id = ?", (aplicacion_id,))
        conn.commit()

        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return {'success': True, 'message': f'✓ Aplicación ID {aplicacion_id} eliminada'}
        else:
            cursor.close()
            conn.close()
            return {'success': False, 'message': f'No se encontró aplicación con ID {aplicacion_id}'}

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print(f"[ERROR] eliminar_aplicacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def obtener_aplicaciones_por_vacante(vacante_id: int) -> list:
    """Obtiene todas las aplicaciones asociadas a una vacante específica."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id, a.vacante_id, v.empresa, v.cargo, v.modalidad,
                a.fecha_aplicacion, a.estado, a.nombre_recruiter,
                a.email_recruiter, a.telefono_recruiter, a.notas, a.fecha_registro
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.vacante_id = v.id
            WHERE a.vacante_id = ?
            ORDER BY a.fecha_aplicacion DESC
        """, (vacante_id,))

        aplicaciones = []
        for row in cursor.fetchall():
            aplicaciones.append({
                'id': row[0], 'vacante_id': row[1], 'empresa': row[2],
                'cargo': row[3], 'modalidad': row[4],
                'fecha_aplicacion': row[5], 'estado': row[6],
                'nombre_recruiter': row[7], 'email_recruiter': row[8],
                'telefono_recruiter': row[9], 'notas': row[10],
                'fecha_registro': row[11],
            })

        cursor.close()
        conn.close()
        return aplicaciones

    except Exception as e:
        print(f"[ERROR] obtener_aplicaciones_por_vacante: {e}")
        return []

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def contar_aplicaciones_por_estado() -> Dict:
    """
    Retorna un dict con el conteo de aplicaciones por estado.
    Útil para estadísticas del dashboard.
    """
    conn = get_connection()
    if not conn:
        return {
            'Pending': 0, 'Applied': 0, 'Technical Test': 0,
            'In Interview': 0, 'Done': 0, 'Rejected': 0, 'Open Offer': 0, 'Total': 0
        }

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT estado, COUNT(*) as total
            FROM aplicaciones
            GROUP BY estado
        """)

        conteos = {
            'Pending': 0, 'Applied': 0, 'Technical Test': 0,
            'In Interview': 0, 'Done': 0, 'Rejected': 0, 'Open Offer': 0
        }
        for row in cursor.fetchall():
            conteos[row[0]] = row[1]

        conteos['Total'] = sum(conteos.values())
        cursor.close()
        conn.close()
        return conteos

    except Exception as e:
        print(f"[ERROR] contar_aplicaciones_por_estado: {e}")
        return {'Pendiente': 0, 'Entrevista': 0, 'Rechazado': 0, 'Oferta': 0, 'Total': 0}

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass


def obtener_vacantes_sin_aplicacion() -> list:
    """
    Retorna vacantes que todavía NO tienen aplicación registrada.
    Útil para el dropdown del formulario de nueva aplicación.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.empresa, v.cargo, v.modalidad
            FROM vacantes v
            WHERE v.id NOT IN (SELECT vacante_id FROM aplicaciones)
            ORDER BY v.fecha_registro DESC
        """)

        vacantes = []
        for row in cursor.fetchall():
            vacantes.append({
                'id':        row[0],
                'empresa':   row[1],
                'cargo':     row[2],
                'modalidad': row[3],
            })

        cursor.close()
        conn.close()
        return vacantes

    except Exception as e:
        print(f"[ERROR] obtener_vacantes_sin_aplicacion: {e}")
        return []

    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass
