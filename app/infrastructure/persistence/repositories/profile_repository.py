"""Profile repository implemented directly on top of pyodbc."""

from __future__ import annotations

import logging
from typing import Optional

from app.infrastructure.persistence.connection import get_connection

logger = logging.getLogger(__name__)


class ProfileRepository:
    """Persistence access for the user profile aggregate."""

    @staticmethod
    def _close(cursor=None, conn=None) -> None:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    @staticmethod
    def _clean(value):
        return value.strip() if value and str(value).strip() else None

    def get_active_profile(self) -> Optional[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, nombre, titulo_profesional, ciudad, direccion,
                       celular, correo, perfil_linkedin, perfil_github,
                       nivel_actual, anos_experiencia,
                       salario_min, salario_max, moneda,
                       modalidades_aceptadas,
                       fecha_creacion, fecha_actualizacion
                FROM perfil_usuario
                WHERE activo = 1
                """
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "nombre": row[1],
                "titulo_profesional": row[2],
                "ciudad": row[3],
                "direccion": row[4],
                "celular": row[5],
                "correo": row[6],
                "perfil_linkedin": row[7],
                "perfil_github": row[8],
                "nivel_actual": row[9],
                "anos_experiencia": row[10],
                "salario_min": row[11],
                "salario_max": row[12],
                "moneda": row[13],
                "modalidades_aceptadas": row[14],
                "fecha_creacion": row[15],
                "fecha_actualizacion": row[16],
            }
        except Exception:
            logger.exception("Error obteniendo perfil activo")
            return None
        finally:
            self._close(cursor, conn)

    def save_profile(self, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM perfil_usuario WHERE activo = 1")
            existing = cursor.fetchone()

            params = (
                self._clean(datos.get("nombre")),
                self._clean(datos.get("titulo_profesional")),
                self._clean(datos.get("ciudad")),
                self._clean(datos.get("direccion")),
                self._clean(datos.get("celular")),
                self._clean(datos.get("correo")),
                self._clean(datos.get("perfil_linkedin")),
                self._clean(datos.get("perfil_github")),
                datos.get("nivel_actual", "Mid"),
                datos.get("anos_experiencia", 0),
                datos.get("salario_min"),
                datos.get("salario_max"),
                datos.get("moneda", "COP"),
                datos.get("modalidades_aceptadas", "Remoto,Híbrido,Presencial"),
            )

            if existing:
                perfil_id = existing[0]
                cursor.execute(
                    """
                    UPDATE perfil_usuario SET
                        nombre = ?,
                        titulo_profesional = ?,
                        ciudad = ?,
                        direccion = ?,
                        celular = ?,
                        correo = ?,
                        perfil_linkedin = ?,
                        perfil_github = ?,
                        nivel_actual = ?,
                        anos_experiencia = ?,
                        salario_min = ?,
                        salario_max = ?,
                        moneda = ?,
                        modalidades_aceptadas = ?,
                        fecha_actualizacion = GETDATE()
                    WHERE id = ?
                    """,
                    (*params, perfil_id),
                )
                conn.commit()
                return {"success": True, "message": "✓ Perfil actualizado correctamente", "id": perfil_id}

            cursor.execute(
                """
                INSERT INTO perfil_usuario (
                    nombre, titulo_profesional, ciudad, direccion,
                    celular, correo, perfil_linkedin, perfil_github,
                    nivel_actual, anos_experiencia,
                    salario_min, salario_max, moneda, modalidades_aceptadas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                params,
            )
            cursor.execute("SELECT @@IDENTITY AS id")
            perfil_id = int(cursor.fetchone()[0])
            conn.commit()
            return {"success": True, "message": "✓ Perfil creado correctamente", "id": perfil_id}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error guardando perfil")
            return {"success": False, "message": f"Error en BD: {exc}", "id": None}
        finally:
            self._close(cursor, conn)

    def get_skills(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, categoria, skill, nivel
                FROM perfil_skills
                WHERE perfil_id = ?
                ORDER BY categoria, skill
                """,
                (perfil_id,),
            )
            return [
                {"id": row[0], "categoria": row[1], "skill": row[2], "nivel": row[3]}
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo skills del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_skill(self, perfil_id: int, categoria: str, skill: str, nivel: str) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_skills (perfil_id, categoria, skill, nivel)
                VALUES (?, ?, ?, ?)
                """,
                (perfil_id, categoria.strip(), skill.strip(), nivel.strip()),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Skill "{skill}" agregada'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando skill al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_skill(self, skill_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_skills WHERE id = ?", (skill_id,))
            conn.commit()
            return {"success": True, "message": "✓ Skill eliminada"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando skill %s", skill_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_experiences(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, cargo, empresa, ciudad, fecha_inicio, fecha_fin,
                       es_trabajo_actual, descripcion_empresa, funciones, logros
                FROM perfil_experiencia_laboral
                WHERE perfil_id = ?
                ORDER BY es_trabajo_actual DESC, fecha_inicio DESC
                """,
                (perfil_id,),
            )
            return [
                {
                    "id": row[0],
                    "cargo": row[1],
                    "empresa": row[2],
                    "ciudad": row[3],
                    "fecha_inicio": row[4],
                    "fecha_fin": row[5],
                    "es_trabajo_actual": bool(row[6]),
                    "descripcion_empresa": row[7],
                    "funciones": row[8],
                    "logros": row[9],
                }
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo experiencias del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_experience(self, perfil_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_experiencia_laboral (
                    perfil_id, cargo, empresa, ciudad,
                    fecha_inicio, fecha_fin, es_trabajo_actual,
                    descripcion_empresa, funciones, logros
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfil_id,
                    self._clean(datos.get("cargo")),
                    self._clean(datos.get("empresa")),
                    self._clean(datos.get("ciudad")),
                    datos.get("fecha_inicio"),
                    datos.get("fecha_fin") if not datos.get("es_trabajo_actual") else None,
                    1 if datos.get("es_trabajo_actual") else 0,
                    self._clean(datos.get("descripcion_empresa")),
                    self._clean(datos.get("funciones")),
                    self._clean(datos.get("logros")),
                ),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Experiencia en "{datos.get("empresa")}" agregada'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando experiencia al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def update_experience(self, exp_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE perfil_experiencia_laboral SET
                    cargo = ?,
                    empresa = ?,
                    ciudad = ?,
                    descripcion_empresa = ?,
                    fecha_inicio = ?,
                    fecha_fin = ?,
                    es_trabajo_actual = ?,
                    funciones = ?,
                    logros = ?,
                    fecha_actualizacion = GETDATE()
                WHERE id = ?
                """,
                (
                    self._clean(datos.get("cargo")),
                    self._clean(datos.get("empresa")),
                    self._clean(datos.get("ciudad")),
                    self._clean(datos.get("descripcion_empresa")),
                    datos.get("fecha_inicio"),
                    datos.get("fecha_fin") if not datos.get("es_trabajo_actual") else None,
                    1 if datos.get("es_trabajo_actual") else 0,
                    self._clean(datos.get("funciones")),
                    self._clean(datos.get("logros")),
                    exp_id,
                ),
            )
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": "✓ Experiencia actualizada correctamente"}
            return {"success": False, "message": f"No se encontro experiencia con ID {exp_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error actualizando experiencia %s", exp_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_experience(self, exp_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_experiencia_laboral WHERE id = ?", (exp_id,))
            conn.commit()
            return {"success": True, "message": "✓ Experiencia eliminada"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando experiencia %s", exp_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_projects(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, nombre, empresa, ciudad, fecha_inicio, fecha_fin,
                       es_proyecto_actual, stack, funciones, logros, url_repositorio
                FROM perfil_proyectos
                WHERE perfil_id = ?
                ORDER BY es_proyecto_actual DESC, fecha_inicio DESC
                """,
                (perfil_id,),
            )
            return [
                {
                    "id": row[0],
                    "nombre": row[1],
                    "empresa": row[2],
                    "ciudad": row[3],
                    "fecha_inicio": row[4],
                    "fecha_fin": row[5],
                    "es_proyecto_actual": bool(row[6]),
                    "stack": row[7],
                    "funciones": row[8],
                    "logros": row[9],
                    "url_repositorio": row[10],
                }
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo proyectos del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_project(self, perfil_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_proyectos (
                    perfil_id, nombre, empresa, ciudad,
                    fecha_inicio, fecha_fin, es_proyecto_actual,
                    stack, funciones, logros, url_repositorio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfil_id,
                    self._clean(datos.get("nombre")),
                    self._clean(datos.get("empresa")),
                    self._clean(datos.get("ciudad")),
                    datos.get("fecha_inicio"),
                    datos.get("fecha_fin") if not datos.get("es_proyecto_actual") else None,
                    1 if datos.get("es_proyecto_actual") else 0,
                    self._clean(datos.get("stack")),
                    self._clean(datos.get("funciones")),
                    self._clean(datos.get("logros")),
                    self._clean(datos.get("url_repositorio")),
                ),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Proyecto "{datos.get("nombre")}" agregado'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando proyecto al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_project(self, proyecto_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_proyectos WHERE id = ?", (proyecto_id,))
            conn.commit()
            return {"success": True, "message": "✓ Proyecto eliminado"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando proyecto %s", proyecto_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_education(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, titulo, institucion, ciudad, nivel,
                       fecha_inicio, fecha_fin, status
                FROM perfil_educacion
                WHERE perfil_id = ?
                ORDER BY fecha_inicio DESC
                """,
                (perfil_id,),
            )
            return [
                {
                    "id": row[0],
                    "titulo": row[1],
                    "institucion": row[2],
                    "ciudad": row[3],
                    "nivel": row[4],
                    "fecha_inicio": row[5],
                    "fecha_fin": row[6],
                    "status": row[7],
                }
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo educacion del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_education(self, perfil_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_educacion (
                    perfil_id, titulo, institucion, ciudad,
                    nivel, fecha_inicio, fecha_fin, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfil_id,
                    self._clean(datos.get("titulo")),
                    self._clean(datos.get("institucion")),
                    self._clean(datos.get("ciudad")),
                    datos.get("nivel", "Pregrado"),
                    datos.get("fecha_inicio"),
                    datos.get("fecha_fin"),
                    datos.get("status", "Completado"),
                ),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Educación "{datos.get("titulo")}" agregada'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando educacion al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_education(self, edu_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_educacion WHERE id = ?", (edu_id,))
            conn.commit()
            return {"success": True, "message": "✓ Educación eliminada"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando educacion %s", edu_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_courses(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, titulo, institucion, fecha_inicio, fecha_fin,
                       status, url_certificado
                FROM perfil_cursos
                WHERE perfil_id = ?
                ORDER BY fecha_fin DESC, fecha_inicio DESC
                """,
                (perfil_id,),
            )
            return [
                {
                    "id": row[0],
                    "titulo": row[1],
                    "institucion": row[2],
                    "fecha_inicio": row[3],
                    "fecha_fin": row[4],
                    "status": row[5],
                    "url_certificado": row[6],
                }
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo cursos del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_course(self, perfil_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_cursos (
                    perfil_id, titulo, institucion,
                    fecha_inicio, fecha_fin, status, url_certificado
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfil_id,
                    self._clean(datos.get("titulo")),
                    self._clean(datos.get("institucion")),
                    datos.get("fecha_inicio"),
                    datos.get("fecha_fin"),
                    datos.get("status", "Completado"),
                    self._clean(datos.get("url_certificado")),
                ),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Curso "{datos.get("titulo")}" agregado'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando curso al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_course(self, curso_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_cursos WHERE id = ?", (curso_id,))
            conn.commit()
            return {"success": True, "message": "✓ Curso eliminado"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando curso %s", curso_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_certifications(self, perfil_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, titulo, institucion, fecha_obtencion,
                       fecha_vencimiento, status, url_certificado
                FROM perfil_certificaciones
                WHERE perfil_id = ?
                ORDER BY fecha_obtencion DESC
                """,
                (perfil_id,),
            )
            return [
                {
                    "id": row[0],
                    "titulo": row[1],
                    "institucion": row[2],
                    "fecha_obtencion": row[3],
                    "fecha_vencimiento": row[4],
                    "status": row[5],
                    "url_certificado": row[6],
                }
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo certificaciones del perfil %s", perfil_id)
            return []
        finally:
            self._close(cursor, conn)

    def add_certification(self, perfil_id: int, datos: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO perfil_certificaciones (
                    perfil_id, titulo, institucion,
                    fecha_obtencion, fecha_vencimiento, status, url_certificado
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfil_id,
                    self._clean(datos.get("titulo")),
                    self._clean(datos.get("institucion")),
                    datos.get("fecha_obtencion"),
                    datos.get("fecha_vencimiento"),
                    datos.get("status", "Vigente"),
                    self._clean(datos.get("url_certificado")),
                ),
            )
            conn.commit()
            return {"success": True, "message": f'✓ Certificación "{datos.get("titulo")}" agregada'}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error agregando certificacion al perfil %s", perfil_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete_certification(self, cert_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM perfil_certificaciones WHERE id = ?", (cert_id,))
            conn.commit()
            return {"success": True, "message": "✓ Certificación eliminada"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando certificacion %s", cert_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)
