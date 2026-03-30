"""
services.py

Servicios compartidos para coordinar flujos reutilizables de la aplicacion.
"""

import logging
from contextlib import nullcontext

import database
from modules.analizar_vacante import analizar_vacante

try:
    import streamlit as st
except Exception:  # pragma: no cover - fallback para contextos sin Streamlit
    st = None


logger = logging.getLogger(__name__)


def _mostrar_error_ui(mostrar_ui: bool, mensaje: str) -> None:
    """Muestra errores solo cuando Streamlit esta disponible y habilitado."""
    if mostrar_ui and st is not None:
        st.error(mensaje)


def _spinner_context(mostrar_ui: bool, mensaje: str):
    """Retorna spinner de Streamlit o un context manager vacio."""
    if mostrar_ui and st is not None:
        return st.spinner(mensaje)
    return nullcontext()


def ejecutar_analisis_vacante(vacante_id: int, mostrar_ui: bool = True) -> dict:
    """
    Ejecuta el flujo completo de analisis de afinidad para una vacante.

    Si no existe un perfil activo, omite el analisis sin fallar el flujo.
    """
    vacante = database.obtener_vacante_por_id(vacante_id)
    if not vacante:
        mensaje = f"No se encontro la vacante con ID {vacante_id}."
        _mostrar_error_ui(mostrar_ui, f"❌ {mensaje}")
        return {
            'success': False,
            'analizado': False,
            'omitido': False,
            'message': mensaje,
        }

    perfil = database.obtener_perfil()
    if not perfil:
        mensaje = (
            f"Analisis omitido para vacante {vacante_id}: no existe un perfil activo."
        )
        logger.warning(mensaje)
        return {
            'success': True,
            'analizado': False,
            'omitido': True,
            'message': mensaje,
        }

    perfil_completo = database.obtener_perfil_completo_para_analisis(perfil['id'])
    if not perfil_completo:
        mensaje = "No se pudo cargar tu perfil completo."
        _mostrar_error_ui(mostrar_ui, f"⚠️ {mensaje}")
        return {
            'success': False,
            'analizado': False,
            'omitido': False,
            'message': mensaje,
        }

    with _spinner_context(
        mostrar_ui,
        "🤖 Analizando vacante con IA... esto puede tomar unos segundos",
    ):
        resultado = analizar_vacante(vacante, perfil_completo)

    if not resultado['success']:
        _mostrar_error_ui(mostrar_ui, f"❌ {resultado['message']}")
        return {
            'success': False,
            'analizado': False,
            'omitido': False,
            'message': resultado['message'],
        }

    res_db = database.guardar_analisis_vacante(
        vacante_id=vacante['id'],
        perfil_id=perfil['id'],
        analisis=resultado,
    )

    if not res_db['success']:
        _mostrar_error_ui(mostrar_ui, f"❌ Error al guardar: {res_db['message']}")
        return {
            'success': False,
            'analizado': False,
            'omitido': False,
            'message': res_db['message'],
        }

    if mostrar_ui and st is not None:
        st.success("✅ Análisis completado")

    return {
        'success': True,
        'analizado': True,
        'omitido': False,
        'message': res_db['message'],
        'analisis': resultado,
    }
