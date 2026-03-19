"""
api.py — FastAPI endpoint para la extensión de Chrome
Corre en paralelo a Streamlit en el puerto 8001.

Arrancar con:
    uvicorn api:app --port 8001 --reload

Requiere instalar:
    pip install fastapi uvicorn
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Asegurar que database.py sea importable desde este archivo
sys.path.insert(0, os.path.dirname(__file__))
import database

# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="CVs-Optimizador API",
    description="Endpoint local para la extensión de Chrome",
    version="1.0.0",
)

# CORS: permite que la extensión de Chrome (origen chrome-extension://)
# haga requests a este servidor local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # En local está bien; en producción restringir
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────

class VacantePayload(BaseModel):
    empresa:     str
    cargo:       str
    modalidad:   str                  # "Remoto" | "Presencial" | "Híbrido"
    link:        Optional[str] = None
    descripcion: str


class VacanteResponse(BaseModel):
    success: bool
    message: str
    id:      Optional[int] = None


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """
    Health check — la extensión lo usa para saber si la API está activa
    antes de intentar guardar.
    """
    db_ok = database.test_connection()
    return {
        "status": "ok" if db_ok else "db_error",
        "db_connected": db_ok,
        "message": "API activa" if db_ok else "API activa pero sin conexión a BD",
    }


@app.post("/vacantes", response_model=VacanteResponse)
def crear_vacante(payload: VacantePayload):
    """
    Recibe los datos de una vacante desde la extensión de Chrome
    y los inserta en la base de datos usando database.py existente.
    """
    # Normalizar modalidad — LinkedIn puede devolver variaciones
    modalidad_map = {
        "remote":     "Remoto",
        "remoto":     "Remoto",
        "on-site":    "Presencial",
        "presencial": "Presencial",
        "on site":    "Presencial",
        "hybrid":     "Híbrido",
        "híbrido":    "Híbrido",
        "hibrido":    "Híbrido",
    }
    modalidad_norm = modalidad_map.get(
        payload.modalidad.lower().strip(),
        "Remoto"          # fallback si LinkedIn devuelve algo inesperado
    )

    resultado = database.insertar_vacante(
        empresa=payload.empresa.strip(),
        cargo=payload.cargo.strip(),
        modalidad=modalidad_norm,
        link=payload.link,
        descripcion=payload.descripcion.strip(),
    )

    if not resultado["success"]:
        raise HTTPException(status_code=500, detail=resultado["message"])

    return VacanteResponse(
        success=True,
        message=resultado["message"],
        id=resultado["id"],
    )
