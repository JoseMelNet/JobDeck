"""Vacancy analysis repository implemented directly on top of pyodbc."""

from __future__ import annotations

import json
import logging
from typing import Optional

from app.infrastructure.persistence.connection import get_connection

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """Persistence access for analysis results."""

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
    def _jdump(value):
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return value or "[]"

    @staticmethod
    def _sjson(value):
        if not value:
            return []
        try:
            return json.loads(value)
        except Exception:
            return value

    def save(self, vacante_id: int, perfil_id: int, analisis: dict) -> dict:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM vacantes_analisis WHERE vacante_id = ?", (vacante_id,))
            existing = cursor.fetchone()

            params = (
                perfil_id,
                self._jdump(analisis.get("skills_requeridas", [])),
                self._jdump(analisis.get("skills_blandas_detectadas", [])),
                analisis.get("seniority_inferido", "No especificado"),
                analisis.get("justificacion_seniority"),
                analisis.get("modalidad_detectada"),
                analisis.get("salario_detectado"),
                self._jdump(analisis.get("idiomas_requeridos", [])),
                analisis.get("tipo_real_de_rol"),
                analisis.get("afinidad_general"),
                analisis.get("justificacion_afinidad"),
                self._jdump(analisis.get("fortalezas_principales", [])),
                self._jdump(analisis.get("riesgos_principales", [])),
                analisis.get("encaje_estrategico"),
                analisis.get("justificacion_decision"),
                analisis.get("decision_aplicacion"),
                self._jdump(analisis.get("ajustes_cv_recomendados", [])),
                analisis.get("score_total", 0),
                analisis.get("score_skills_tecnicas", 0),
                analisis.get("score_seniority", 0),
                analisis.get("score_modalidad", 0),
                analisis.get("score_idiomas", 0),
                analisis.get("score_skills_blandas", 0),
                analisis.get("score_global", 0),
                analisis.get("semaforo", "gris"),
                analisis.get("resumen_analisis"),
                self._jdump(analisis.get("skills_match", [])),
                self._jdump(analisis.get("skills_gap", [])),
                analisis.get("aspiracion_salarial_sugerida"),
            )

            if existing:
                cursor.execute(
                    """
                    UPDATE vacantes_analisis SET
                        perfil_id = ?,
                        skills_requeridas = ?,
                        skills_blandas_detectadas = ?,
                        seniority_inferido = ?,
                        justificacion_seniority = ?,
                        modalidad_detectada = ?,
                        salario_detectado = ?,
                        idiomas_requeridos = ?,
                        tipo_real_de_rol = ?,
                        afinidad_general = ?,
                        justificacion_afinidad = ?,
                        fortalezas_principales = ?,
                        riesgos_principales = ?,
                        encaje_estrategico = ?,
                        justificacion_decision = ?,
                        decision_aplicacion = ?,
                        ajustes_cv_recomendados = ?,
                        score_total = ?,
                        score_skills_tecnicas = ?,
                        score_seniority = ?,
                        score_modalidad = ?,
                        score_idiomas = ?,
                        score_skills_blandas = ?,
                        score_global = ?,
                        semaforo = ?,
                        resumen_analisis = ?,
                        skills_match = ?,
                        skills_gap = ?,
                        aspiracion_salarial_sugerida = ?,
                        fecha_analisis = GETDATE()
                    WHERE vacante_id = ?
                    """,
                    (*params, vacante_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO vacantes_analisis (
                        perfil_id,
                        skills_requeridas, skills_blandas_detectadas,
                        seniority_inferido, justificacion_seniority,
                        modalidad_detectada, salario_detectado, idiomas_requeridos,
                        tipo_real_de_rol,
                        afinidad_general, justificacion_afinidad,
                        fortalezas_principales, riesgos_principales,
                        encaje_estrategico, justificacion_decision,
                        decision_aplicacion, ajustes_cv_recomendados,
                        score_total, score_skills_tecnicas, score_seniority,
                        score_modalidad, score_idiomas, score_skills_blandas,
                        score_global, semaforo,
                        resumen_analisis, skills_match, skills_gap,
                        aspiracion_salarial_sugerida,
                        vacante_id
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (*params, vacante_id),
                )

            conn.commit()
            return {"success": True, "message": "✓ Análisis guardado correctamente"}
        except Exception as exc:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.exception("Error guardando analisis de vacante %s", vacante_id)
            return {"success": False, "message": f"Error en BD: {exc}"}
        finally:
            self._close(cursor, conn)

    def get_by_vacancy_id(self, vacante_id: int) -> Optional[dict]:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    score_total, score_global, semaforo,
                    seniority_inferido, justificacion_seniority,
                    modalidad_detectada, salario_detectado,
                    resumen_analisis,
                    skills_match, skills_gap,
                    skills_requeridas, skills_blandas_detectadas,
                    idiomas_requeridos,
                    aspiracion_salarial_sugerida,
                    score_skills_tecnicas, score_seniority,
                    score_modalidad, score_idiomas, score_skills_blandas,
                    tipo_real_de_rol,
                    afinidad_general, justificacion_afinidad,
                    fortalezas_principales, riesgos_principales,
                    encaje_estrategico, justificacion_decision,
                    decision_aplicacion, ajustes_cv_recomendados,
                    fecha_analisis
                FROM vacantes_analisis
                WHERE vacante_id = ?
                """,
                (vacante_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "score_total": float(row[0]) if row[0] else 0,
                "score_global": float(row[1]) if row[1] else 0,
                "semaforo": row[2] or "gris",
                "seniority_inferido": row[3],
                "justificacion_seniority": row[4],
                "modalidad_detectada": row[5],
                "salario_detectado": row[6],
                "resumen_analisis": row[7],
                "skills_match": self._sjson(row[8]),
                "skills_gap": self._sjson(row[9]),
                "skills_requeridas": self._sjson(row[10]),
                "skills_blandas_detectadas": self._sjson(row[11]),
                "idiomas_requeridos": self._sjson(row[12]),
                "aspiracion_salarial_sugerida": row[13],
                "score_skills_tecnicas": float(row[14]) if row[14] else 0,
                "score_seniority": float(row[15]) if row[15] else 0,
                "score_modalidad": float(row[16]) if row[16] else 0,
                "score_idiomas": float(row[17]) if row[17] else 0,
                "score_skills_blandas": float(row[18]) if row[18] else 0,
                "tipo_real_de_rol": row[19],
                "afinidad_general": row[20],
                "justificacion_afinidad": row[21],
                "fortalezas_principales": self._sjson(row[22]),
                "riesgos_principales": self._sjson(row[23]),
                "encaje_estrategico": row[24],
                "justificacion_decision": row[25],
                "decision_aplicacion": row[26],
                "ajustes_cv_recomendados": self._sjson(row[27]),
                "fecha_analisis": row[28],
            }
        except Exception:
            logger.exception("Error obteniendo analisis de vacante %s", vacante_id)
            return None
        finally:
            self._close(cursor, conn)
