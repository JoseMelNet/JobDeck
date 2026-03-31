"""Application repository implemented directly on top of pyodbc."""

from __future__ import annotations

import logging
from typing import Optional

from app.domain.enums.application_status import APPLICATION_STATUSES
from app.infrastructure.persistence.connection import get_connection

logger = logging.getLogger(__name__)


class ApplicationRepository:
    """Persistence access for job applications."""

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

    @staticmethod
    def _row_to_application(row, include_link: bool = True) -> dict:
        if include_link:
            return {
                "id": row[0],
                "vacante_id": row[1],
                "empresa": row[2],
                "cargo": row[3],
                "modalidad": row[4],
                "link": row[5],
                "fecha_aplicacion": row[6],
                "estado": row[7],
                "nombre_recruiter": row[8],
                "email_recruiter": row[9],
                "telefono_recruiter": row[10],
                "notas": row[11],
                "fecha_registro": row[12],
            }
        return {
            "id": row[0],
            "vacante_id": row[1],
            "empresa": row[2],
            "cargo": row[3],
            "modalidad": row[4],
            "fecha_aplicacion": row[5],
            "estado": row[6],
            "nombre_recruiter": row[7],
            "email_recruiter": row[8],
            "telefono_recruiter": row[9],
            "notas": row[10],
            "fecha_registro": row[11],
        }

    def create(self, **payload) -> dict:
        conn = None
        cursor = None
        estado = payload.get("estado")
        if estado not in APPLICATION_STATUSES:
            return {
                "success": False,
                "message": f"Estado invalido. Usa: {', '.join(APPLICATION_STATUSES)}",
                "id": None,
            }

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM aplicaciones WHERE vacante_id = ?", (payload["vacante_id"],))
            if cursor.fetchone():
                return {
                    "success": False,
                    "message": "⚠️ Ya existe una aplicación registrada para esta vacante.",
                    "id": None,
                }

            cursor.execute(
                """
                INSERT INTO aplicaciones (
                    vacante_id, fecha_aplicacion, estado, nombre_recruiter,
                    email_recruiter, telefono_recruiter, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["vacante_id"],
                    payload["fecha_aplicacion"],
                    estado,
                    self._clean(payload.get("nombre_recruiter")),
                    self._clean(payload.get("email_recruiter")),
                    self._clean(payload.get("telefono_recruiter")),
                    self._clean(payload.get("notas")),
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS id;")
            result = cursor.fetchone()
            if not result or result[0] is None:
                conn.rollback()
                return {
                    "success": False,
                    "message": "Error: No se pudo obtener el ID de la aplicación",
                    "id": None,
                }

            application_id = int(result[0])
            conn.commit()
            return {
                "success": True,
                "message": f"✓ Aplicación guardada exitosamente (ID: {application_id})",
                "id": application_id,
            }
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error creando aplicacion")
            return {"success": False, "message": f"Error en BD: {exc}", "id": None}
        finally:
            self._close(cursor, conn)

    def list_all(self) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
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
                """
            )
            return [self._row_to_application(row, include_link=True) for row in cursor.fetchall()]
        except Exception:
            logger.exception("Error obteniendo aplicaciones")
            return []
        finally:
            self._close(cursor, conn)

    def get_by_id(self, aplicacion_id: int) -> Optional[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    a.id, a.vacante_id, v.empresa, v.cargo, v.modalidad, v.link,
                    a.fecha_aplicacion, a.estado, a.nombre_recruiter,
                    a.email_recruiter, a.telefono_recruiter, a.notas, a.fecha_registro
                FROM aplicaciones a
                INNER JOIN vacantes v ON a.vacante_id = v.id
                WHERE a.id = ?
                """,
                (aplicacion_id,),
            )
            row = cursor.fetchone()
            return self._row_to_application(row, include_link=True) if row else None
        except Exception:
            logger.exception("Error obteniendo aplicacion %s", aplicacion_id)
            return None
        finally:
            self._close(cursor, conn)

    def update_status(self, aplicacion_id: int, nuevo_estado: str) -> dict:
        conn = None
        cursor = None
        if nuevo_estado not in APPLICATION_STATUSES:
            return {
                "success": False,
                "message": f"Estado invalido. Opciones: {', '.join(APPLICATION_STATUSES)}",
            }

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE aplicaciones SET estado = ? WHERE id = ?", (nuevo_estado, aplicacion_id))
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": f'✓ Estado actualizado a "{nuevo_estado}"'}
            return {"success": False, "message": f"No se encontro aplicación con ID {aplicacion_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error actualizando estado de aplicacion %s", aplicacion_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def update(self, aplicacion_id: int, **payload) -> dict:
        conn = None
        cursor = None
        estado = payload.get("estado")
        if estado not in APPLICATION_STATUSES:
            return {
                "success": False,
                "message": f"Estado invalido. Opciones: {', '.join(APPLICATION_STATUSES)}",
            }

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE aplicaciones
                SET estado = ?,
                    nombre_recruiter = ?,
                    email_recruiter = ?,
                    telefono_recruiter = ?,
                    notas = ?
                WHERE id = ?
                """,
                (
                    estado,
                    self._clean(payload.get("nombre_recruiter")),
                    self._clean(payload.get("email_recruiter")),
                    self._clean(payload.get("telefono_recruiter")),
                    self._clean(payload.get("notas")),
                    aplicacion_id,
                ),
            )
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": "✓ Aplicación actualizada correctamente"}
            return {"success": False, "message": f"No se encontro aplicación con ID {aplicacion_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error actualizando aplicacion %s", aplicacion_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def delete(self, aplicacion_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM aplicaciones WHERE id = ?", (aplicacion_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": f"✓ Aplicación ID {aplicacion_id} eliminada"}
            return {"success": False, "message": f"No se encontro aplicación con ID {aplicacion_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando aplicacion %s", aplicacion_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def list_by_vacancy(self, vacante_id: int) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    a.id, a.vacante_id, v.empresa, v.cargo, v.modalidad,
                    a.fecha_aplicacion, a.estado, a.nombre_recruiter,
                    a.email_recruiter, a.telefono_recruiter, a.notas, a.fecha_registro
                FROM aplicaciones a
                INNER JOIN vacantes v ON a.vacante_id = v.id
                WHERE a.vacante_id = ?
                ORDER BY a.fecha_aplicacion DESC
                """,
                (vacante_id,),
            )
            return [self._row_to_application(row, include_link=False) for row in cursor.fetchall()]
        except Exception:
            logger.exception("Error obteniendo aplicaciones por vacante %s", vacante_id)
            return []
        finally:
            self._close(cursor, conn)

    def count_by_status(self) -> dict:
        conn = None
        cursor = None
        conteos = {estado: 0 for estado in APPLICATION_STATUSES}
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT estado, COUNT(*) as total
                FROM aplicaciones
                GROUP BY estado
                """
            )
            for row in cursor.fetchall():
                conteos[row[0]] = row[1]
            conteos["Total"] = sum(conteos.values())
            return conteos
        except Exception:
            logger.exception("Error contando aplicaciones por estado")
            conteos["Total"] = 0
            return conteos
        finally:
            self._close(cursor, conn)
