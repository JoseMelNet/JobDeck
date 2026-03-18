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

"""
database_perfil.py
Funciones CRUD para las tablas del perfil de usuario.

Tablas cubiertas:
  - perfil_usuario
  - perfil_skills
  - perfil_experiencia_laboral
  - perfil_proyectos
  - perfil_educacion
  - perfil_cursos
  - perfil_certificaciones
"""

# ============================================================
# PERFIL USUARIO — datos personales y configuración base
# ============================================================

def obtener_perfil() -> Optional[Dict]:
    """
    Obtiene el perfil activo del usuario.
    Retorna None si no existe ningún perfil aún.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, titulo_profesional, ciudad, direccion,
                   celular, correo, perfil_linkedin, perfil_github,
                   nivel_actual, anos_experiencia,
                   salario_min, salario_max, moneda,
                   modalidades_aceptadas,
                   fecha_creacion, fecha_actualizacion
            FROM perfil_usuario
            WHERE activo = 1
        """)
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0], 'nombre': row[1], 'titulo_profesional': row[2],
                'ciudad': row[3], 'direccion': row[4], 'celular': row[5],
                'correo': row[6], 'perfil_linkedin': row[7], 'perfil_github': row[8],
                'nivel_actual': row[9], 'anos_experiencia': row[10],
                'salario_min': row[11], 'salario_max': row[12], 'moneda': row[13],
                'modalidades_aceptadas': row[14],
                'fecha_creacion': row[15], 'fecha_actualizacion': row[16],
            }
        return None
    except Exception as e:
        print(f"[ERROR] obtener_perfil: {e}")
        return None
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def guardar_perfil(datos: Dict) -> Dict:
    """
    Crea o actualiza el perfil del usuario.
    Si ya existe un perfil activo lo actualiza (UPDATE).
    Si no existe lo crea (INSERT).

    datos: dict con las claves del perfil_usuario.
    Retorna {'success': bool, 'message': str, 'id': int}
    """
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD', 'id': None}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()

        # ¿Ya existe un perfil activo?
        cursor.execute("SELECT id FROM perfil_usuario WHERE activo = 1")
        existing = cursor.fetchone()

        if existing:
            perfil_id = existing[0]
            cursor.execute("""
                UPDATE perfil_usuario SET
                    nombre                = ?,
                    titulo_profesional    = ?,
                    ciudad                = ?,
                    direccion             = ?,
                    celular               = ?,
                    correo                = ?,
                    perfil_linkedin       = ?,
                    perfil_github         = ?,
                    nivel_actual          = ?,
                    anos_experiencia      = ?,
                    salario_min           = ?,
                    salario_max           = ?,
                    moneda                = ?,
                    modalidades_aceptadas = ?,
                    fecha_actualizacion   = GETDATE()
                WHERE id = ?
            """, (
                c(datos.get('nombre')),
                c(datos.get('titulo_profesional')),
                c(datos.get('ciudad')),
                c(datos.get('direccion')),
                c(datos.get('celular')),
                c(datos.get('correo')),
                c(datos.get('perfil_linkedin')),
                c(datos.get('perfil_github')),
                datos.get('nivel_actual', 'Mid'),
                datos.get('anos_experiencia', 0),
                datos.get('salario_min'),
                datos.get('salario_max'),
                datos.get('moneda', 'COP'),
                datos.get('modalidades_aceptadas', 'Remoto,Híbrido,Presencial'),
                perfil_id
            ))
            conn.commit()
            return {'success': True, 'message': '✓ Perfil actualizado correctamente', 'id': perfil_id}
        else:
            cursor.execute("""
                INSERT INTO perfil_usuario (
                    nombre, titulo_profesional, ciudad, direccion,
                    celular, correo, perfil_linkedin, perfil_github,
                    nivel_actual, anos_experiencia,
                    salario_min, salario_max, moneda, modalidades_aceptadas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c(datos.get('nombre')),
                c(datos.get('titulo_profesional')),
                c(datos.get('ciudad')),
                c(datos.get('direccion')),
                c(datos.get('celular')),
                c(datos.get('correo')),
                c(datos.get('perfil_linkedin')),
                c(datos.get('perfil_github')),
                datos.get('nivel_actual', 'Mid'),
                datos.get('anos_experiencia', 0),
                datos.get('salario_min'),
                datos.get('salario_max'),
                datos.get('moneda', 'COP'),
                datos.get('modalidades_aceptadas', 'Remoto,Híbrido,Presencial'),
            ))
            cursor.execute("SELECT @@IDENTITY AS id")
            perfil_id = int(cursor.fetchone()[0])
            conn.commit()
            return {'success': True, 'message': '✓ Perfil creado correctamente', 'id': perfil_id}

    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] guardar_perfil: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}', 'id': None}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL SKILLS
# ============================================================

def obtener_skills(perfil_id: int) -> List[Dict]:
    """Obtiene todas las skills del perfil, ordenadas por categoría."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, categoria, skill, nivel
            FROM perfil_skills
            WHERE perfil_id = ?
            ORDER BY categoria, skill
        """, (perfil_id,))
        return [
            {'id': r[0], 'categoria': r[1], 'skill': r[2], 'nivel': r[3]}
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_skills: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_skill(perfil_id: int, categoria: str, skill: str, nivel: str) -> Dict:
    """Inserta una nueva skill para el perfil."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_skills (perfil_id, categoria, skill, nivel)
            VALUES (?, ?, ?, ?)
        """, (perfil_id, categoria.strip(), skill.strip(), nivel.strip()))
        conn.commit()
        return {'success': True, 'message': f'✓ Skill "{skill}" agregada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_skill: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_skill(skill_id: int) -> Dict:
    """Elimina una skill por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_skills WHERE id = ?", (skill_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Skill eliminada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL EXPERIENCIA LABORAL
# ============================================================

def obtener_experiencias(perfil_id: int) -> List[Dict]:
    """Obtiene todas las experiencias laborales, de más reciente a más antigua."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, cargo, empresa, ciudad, fecha_inicio, fecha_fin,
                   es_trabajo_actual, descripcion_empresa, funciones, logros
            FROM perfil_experiencia_laboral
            WHERE perfil_id = ?
            ORDER BY es_trabajo_actual DESC, fecha_inicio DESC
        """, (perfil_id,))
        return [
            {
                'id': r[0], 'cargo': r[1], 'empresa': r[2], 'ciudad': r[3],
                'fecha_inicio': r[4], 'fecha_fin': r[5],
                'es_trabajo_actual': bool(r[6]),
                'descripcion_empresa': r[7], 'funciones': r[8], 'logros': r[9],
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_experiencias: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_experiencia(perfil_id: int, datos: Dict) -> Dict:
    """Inserta una nueva experiencia laboral."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_experiencia_laboral (
                perfil_id, cargo, empresa, ciudad,
                fecha_inicio, fecha_fin, es_trabajo_actual,
                descripcion_empresa, funciones, logros
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            perfil_id,
            c(datos.get('cargo')),
            c(datos.get('empresa')),
            c(datos.get('ciudad')),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin') if not datos.get('es_trabajo_actual') else None,
            1 if datos.get('es_trabajo_actual') else 0,
            c(datos.get('descripcion_empresa')),
            c(datos.get('funciones')),
            c(datos.get('logros')),
        ))
        conn.commit()
        return {'success': True, 'message': f'✓ Experiencia en "{datos.get("empresa")}" agregada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_experiencia: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_experiencia(exp_id: int) -> Dict:
    """Elimina una experiencia laboral por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_experiencia_laboral WHERE id = ?", (exp_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Experiencia eliminada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def actualizar_experiencia(exp_id: int, datos: dict) -> dict:
    """
    Actualiza todos los campos editables de una experiencia laboral.
    """
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE perfil_experiencia_laboral SET
                cargo               = ?,
                empresa             = ?,
                ciudad              = ?,
                descripcion_empresa = ?,
                fecha_inicio        = ?,
                fecha_fin           = ?,
                es_trabajo_actual   = ?,
                funciones           = ?,
                logros              = ?,
                fecha_actualizacion = GETDATE()
            WHERE id = ?
        """, (
            c(datos.get('cargo')),
            c(datos.get('empresa')),
            c(datos.get('ciudad')),
            c(datos.get('descripcion_empresa')),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin') if not datos.get('es_trabajo_actual') else None,
            1 if datos.get('es_trabajo_actual') else 0,
            c(datos.get('funciones')),
            c(datos.get('logros')),
            exp_id
        ))
        conn.commit()

        if cursor.rowcount > 0:
            return {'success': True, 'message': '✓ Experiencia actualizada correctamente'}
        else:
            return {'success': False, 'message': f'No se encontró experiencia con ID {exp_id}'}

    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] actualizar_experiencia: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL PROYECTOS
# ============================================================

def obtener_proyectos(perfil_id: int) -> List[Dict]:
    """Obtiene todos los proyectos del perfil."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, empresa, ciudad, fecha_inicio, fecha_fin,
                   es_proyecto_actual, stack, funciones, logros, url_repositorio
            FROM perfil_proyectos
            WHERE perfil_id = ?
            ORDER BY es_proyecto_actual DESC, fecha_inicio DESC
        """, (perfil_id,))
        return [
            {
                'id': r[0], 'nombre': r[1], 'empresa': r[2], 'ciudad': r[3],
                'fecha_inicio': r[4], 'fecha_fin': r[5],
                'es_proyecto_actual': bool(r[6]),
                'stack': r[7], 'funciones': r[8], 'logros': r[9],
                'url_repositorio': r[10],
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_proyectos: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_proyecto(perfil_id: int, datos: Dict) -> Dict:
    """Inserta un nuevo proyecto."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_proyectos (
                perfil_id, nombre, empresa, ciudad,
                fecha_inicio, fecha_fin, es_proyecto_actual,
                stack, funciones, logros, url_repositorio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            perfil_id,
            c(datos.get('nombre')),
            c(datos.get('empresa')),
            c(datos.get('ciudad')),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin') if not datos.get('es_proyecto_actual') else None,
            1 if datos.get('es_proyecto_actual') else 0,
            c(datos.get('stack')),
            c(datos.get('funciones')),
            c(datos.get('logros')),
            c(datos.get('url_repositorio')),
        ))
        conn.commit()
        return {'success': True, 'message': f'✓ Proyecto "{datos.get("nombre")}" agregado'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_proyecto: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_proyecto(proyecto_id: int) -> Dict:
    """Elimina un proyecto por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_proyectos WHERE id = ?", (proyecto_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Proyecto eliminado'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL EDUCACION
# ============================================================

def obtener_educacion(perfil_id: int) -> List[Dict]:
    """Obtiene toda la formación académica del perfil."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, institucion, ciudad, nivel,
                   fecha_inicio, fecha_fin, status
            FROM perfil_educacion
            WHERE perfil_id = ?
            ORDER BY fecha_inicio DESC
        """, (perfil_id,))
        return [
            {
                'id': r[0], 'titulo': r[1], 'institucion': r[2],
                'ciudad': r[3], 'nivel': r[4],
                'fecha_inicio': r[5], 'fecha_fin': r[6], 'status': r[7],
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_educacion: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_educacion(perfil_id: int, datos: Dict) -> Dict:
    """Inserta un nuevo registro de educación."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_educacion (
                perfil_id, titulo, institucion, ciudad,
                nivel, fecha_inicio, fecha_fin, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            perfil_id,
            c(datos.get('titulo')),
            c(datos.get('institucion')),
            c(datos.get('ciudad')),
            datos.get('nivel', 'Pregrado'),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin'),
            datos.get('status', 'Completado'),
        ))
        conn.commit()
        return {'success': True, 'message': f'✓ Educación "{datos.get("titulo")}" agregada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_educacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_educacion(edu_id: int) -> Dict:
    """Elimina un registro de educación por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_educacion WHERE id = ?", (edu_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Educación eliminada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL CURSOS
# ============================================================

def obtener_cursos(perfil_id: int) -> List[Dict]:
    """Obtiene todos los cursos del perfil."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, institucion, fecha_inicio, fecha_fin,
                   status, url_certificado
            FROM perfil_cursos
            WHERE perfil_id = ?
            ORDER BY fecha_fin DESC, fecha_inicio DESC
        """, (perfil_id,))
        return [
            {
                'id': r[0], 'titulo': r[1], 'institucion': r[2],
                'fecha_inicio': r[3], 'fecha_fin': r[4],
                'status': r[5], 'url_certificado': r[6],
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_cursos: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_curso(perfil_id: int, datos: Dict) -> Dict:
    """Inserta un nuevo curso."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_cursos (
                perfil_id, titulo, institucion,
                fecha_inicio, fecha_fin, status, url_certificado
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            perfil_id,
            c(datos.get('titulo')),
            c(datos.get('institucion')),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin'),
            datos.get('status', 'Completado'),
            c(datos.get('url_certificado')),
        ))
        conn.commit()
        return {'success': True, 'message': f'✓ Curso "{datos.get("titulo")}" agregado'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_curso: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_curso(curso_id: int) -> Dict:
    """Elimina un curso por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_cursos WHERE id = ?", (curso_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Curso eliminado'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


# ============================================================
# PERFIL CERTIFICACIONES
# ============================================================

def obtener_certificaciones(perfil_id: int) -> List[Dict]:
    """Obtiene todas las certificaciones del perfil."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, institucion, fecha_obtencion,
                   fecha_vencimiento, status, url_certificado
            FROM perfil_certificaciones
            WHERE perfil_id = ?
            ORDER BY fecha_obtencion DESC
        """, (perfil_id,))
        return [
            {
                'id': r[0], 'titulo': r[1], 'institucion': r[2],
                'fecha_obtencion': r[3], 'fecha_vencimiento': r[4],
                'status': r[5], 'url_certificado': r[6],
            }
            for r in cursor.fetchall()
        ]
    except Exception as e:
        print(f"[ERROR] obtener_certificaciones: {e}")
        return []
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def insertar_certificacion(perfil_id: int, datos: Dict) -> Dict:
    """Inserta una nueva certificación."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}

    def c(val):
        return val.strip() if val and str(val).strip() else None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO perfil_certificaciones (
                perfil_id, titulo, institucion,
                fecha_obtencion, fecha_vencimiento, status, url_certificado
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            perfil_id,
            c(datos.get('titulo')),
            c(datos.get('institucion')),
            datos.get('fecha_obtencion'),
            datos.get('fecha_vencimiento'),
            datos.get('status', 'Vigente'),
            c(datos.get('url_certificado')),
        ))
        conn.commit()
        return {'success': True, 'message': f'✓ Certificación "{datos.get("titulo")}" agregada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        print(f"[ERROR] insertar_certificacion: {e}")
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass


def eliminar_certificacion(cert_id: int) -> Dict:
    """Elimina una certificación por ID."""
    conn = get_connection()
    if not conn:
        return {'success': False, 'message': 'Sin conexión a BD'}
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM perfil_certificaciones WHERE id = ?", (cert_id,))
        conn.commit()
        return {'success': True, 'message': '✓ Certificación eliminada'}
    except Exception as e:
        try: conn.rollback()
        except: pass
        return {'success': False, 'message': f'Error en BD: {str(e)}'}
    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass