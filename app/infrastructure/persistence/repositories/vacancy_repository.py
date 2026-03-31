"""Vacancy repository implemented directly on top of pyodbc."""

from __future__ import annotations

import logging
from typing import Optional

from app.domain.enums.archive_reason import ARCHIVE_REASONS
from app.domain.enums.modality import MODALITIES
from app.infrastructure.persistence.connection import get_connection

logger = logging.getLogger(__name__)


class VacancyRepository:
    """Persistence access for vacancies."""

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
    def _row_to_vacancy(row) -> dict:
        return {
            "id": row[0],
            "empresa": row[1],
            "cargo": row[2],
            "modalidad": row[3],
            "link": row[4],
            "descripcion": row[5],
            "fecha_registro": row[6],
            "motivo_archivo": row[7] if len(row) > 7 else None,
        }

    def create(
        self,
        *,
        empresa: str,
        cargo: str,
        modalidad: str,
        descripcion: str,
        link: Optional[str] = None,
    ) -> dict:
        conn = None
        cursor = None
        if modalidad not in MODALITIES:
            return {
                "success": False,
                "message": f"Modalidad invalida. Usa: {', '.join(MODALITIES)}",
                "id": None,
            }

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO vacantes (empresa, cargo, modalidad, link, descripcion)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    empresa,
                    cargo,
                    modalidad,
                    link.strip() if link and link.strip() else None,
                    descripcion,
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS id;")
            result = cursor.fetchone()
            if not result or result[0] is None:
                conn.rollback()
                return {
                    "success": False,
                    "message": "Error: No se pudo obtener el ID de la vacante",
                    "id": None,
                }

            vacante_id = int(result[0])
            conn.commit()
            return {
                "success": True,
                "message": f"✓ Vacante guardada exitosamente (ID: {vacante_id})",
                "id": vacante_id,
            }
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error creando vacante")
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
                SELECT id, empresa, cargo, modalidad, link, descripcion, fecha_registro, motivo_archivo
                FROM vacantes
                ORDER BY fecha_registro DESC
                """
            )
            return [self._row_to_vacancy(row) for row in cursor.fetchall()]
        except Exception:
            logger.exception("Error obteniendo vacantes")
            return []
        finally:
            self._close(cursor, conn)

    def get_by_id(self, vacante_id: int) -> Optional[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, empresa, cargo, modalidad, link, descripcion, fecha_registro, motivo_archivo
                FROM vacantes
                WHERE id = ?
                """,
                (vacante_id,),
            )
            row = cursor.fetchone()
            return self._row_to_vacancy(row) if row else None
        except Exception:
            logger.exception("Error obteniendo vacante %s", vacante_id)
            return None
        finally:
            self._close(cursor, conn)

    def delete(self, vacante_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vacantes WHERE id = ?", (vacante_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": f"✓ Vacante ID {vacante_id} eliminada"}
            return {"success": False, "message": f"No se encontro vacante con ID {vacante_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error eliminando vacante %s", vacante_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def count(self) -> int:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vacantes")
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            logger.exception("Error contando vacantes")
            return 0
        finally:
            self._close(cursor, conn)

    def list_without_application(self) -> list[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT v.id, v.empresa, v.cargo, v.modalidad
                FROM vacantes v
                WHERE v.id NOT IN (SELECT vacante_id FROM aplicaciones)
                ORDER BY v.fecha_registro DESC
                """
            )
            return [
                {"id": row[0], "empresa": row[1], "cargo": row[2], "modalidad": row[3]}
                for row in cursor.fetchall()
            ]
        except Exception:
            logger.exception("Error obteniendo vacantes sin aplicacion")
            return []
        finally:
            self._close(cursor, conn)

    def archive(self, vacante_id: int, motivo: str) -> dict:
        conn = None
        cursor = None
        if motivo not in ARCHIVE_REASONS:
            return {"success": False, "message": "Motivo invalido."}

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE vacantes SET motivo_archivo = ? WHERE id = ?", (motivo, vacante_id))
            conn.commit()
            if cursor.rowcount > 0:
                return {"success": True, "message": f"✓ Vacante archivada: {motivo}"}
            return {"success": False, "message": f"No se encontro vacante ID {vacante_id}"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error archivando vacante %s", vacante_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def unarchive(self, vacante_id: int) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE vacantes SET motivo_archivo = NULL WHERE id = ?", (vacante_id,))
            conn.commit()
            return {"success": True, "message": "✓ Vacante reactivada"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error reactivando vacante %s", vacante_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)
