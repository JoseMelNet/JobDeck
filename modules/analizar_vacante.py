"""
modules/analizar_vacante.py  — v2
Motor de análisis de afinidad vacante vs perfil usando OpenAI.

Arquitectura de dos prompts:
  Prompt 1 (extracción): Lee la vacante y extrae datos estructurados
                         Skills, seniority, modalidad, salario, idiomas
  Prompt 2 (evaluación): Actúa como reclutador evaluador y decide
                         afinidad, encaje, decisión de aplicación, ajustes CV

Se llama desde mis_vacantes.py:
    from modules.analizar_vacante import analizar_vacante
    resultado = analizar_vacante(vacante_dict, perfil_dict)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODELO = "gpt-4o-mini"


# ─────────────────────────────────────────────────────────────
# PROMPT 1 — EXTRACCIÓN ESTRUCTURADA
# ─────────────────────────────────────────────────────────────

PROMPT_EXTRACCION = """
Eres un sistema de extracción de datos de vacantes laborales.
Tu tarea es leer una descripción de vacante y extraer información estructurada.

Responde ÚNICAMENTE con un objeto JSON válido. Sin texto adicional, sin markdown.

Estructura exacta:
{
  "tipo_real_de_rol": "Clasificación real del rol (ej: BI Analyst, Data Engineer, Growth Analyst)",
  "seniority_inferido": "Junior|Mid|Senior|No especificado",
  "justificacion_seniority": "Explicación basada en años requeridos, complejidad técnica, autonomía y exposición a stakeholders",
  "modalidad_detectada": "Remoto|Presencial|Híbrido|No especificado",
  "salario_detectado": "texto con el salario o null si no se menciona",
  "idiomas_requeridos": [
    {"idioma": "nombre", "nivel": "nivel requerido o No especificado"}
  ],
  "skills_requeridas": [
    {"skill": "nombre", "tipo": "requerido|deseable"}
  ],
  "skills_blandas_detectadas": ["skill1", "skill2"]
}

Reglas:
- No inventes datos que no están en la descripción
- Para seniority, analiza el contenido real del rol, no solo el título
- Para skills, lista solo las mencionadas explícitamente o claramente implícitas
- Si un campo no aplica o no está disponible, usa null o lista vacía
""".strip()


# ─────────────────────────────────────────────────────────────
# PROMPT 2 — EVALUACIÓN DE RECLUTADOR
# ─────────────────────────────────────────────────────────────

PROMPT_EVALUACION = """
Eres un reclutador senior especializado en roles de Data, BI, Analytics y perfiles técnicos de negocio.
También actúas como asesor de carrera del candidato.

Tu tarea es evaluar si una vacante vale la pena para un candidato específico y producir
un análisis útil para decidir si aplicar o no.

Responde ÚNICAMENTE con un objeto JSON válido. Sin texto adicional, sin markdown.

Estructura exacta:
{
  "afinidad_general": "Alta|Media|Baja",
  "justificacion_afinidad": "Explicación concreta de por qué la afinidad es alta, media o baja",
  "fortalezas_principales": ["fortaleza1", "fortaleza2", "fortaleza3"],
  "riesgos_principales": ["riesgo1", "riesgo2", "riesgo3"],
  "skills_match": ["skills que el candidato SÍ tiene de las requeridas"],
  "skills_gap": ["skills que la vacante pide y el candidato NO tiene"],
  "encaje_estrategico": "Alineado|Parcialmente alineado|Desvía del objetivo",
  "justificacion_encaje": "Por qué esta vacante ayuda o no a la trayectoria del candidato",
  "decision_aplicacion": "Aplicar sí o sí|Aplicar si sobra tiempo|Descartar",
  "justificacion_decision": "Explicación directa y franca de si vale la pena aplicar",
  "ajustes_cv_recomendados": ["ajuste1", "ajuste2", "ajuste3"],
  "aspiracion_salarial_sugerida": "rango sugerido en la moneda del candidato o null",
  "resumen_analisis": "Párrafo sustancial con juicio de reclutamiento real: tipo de rol, afinidad, por qué aplicar o no, fortalezas y gaps principales",
  "scores": {
    "score_skills_tecnicas": 0,
    "score_seniority": 0,
    "score_modalidad": 0,
    "score_idiomas": 0,
    "score_encaje_estrategico": 0
  }
}

Reglas de evaluación:
1. No te limites al título. Infiere el tipo real del rol según responsabilidades y stack.
2. La afinidad depende de: herramientas, seniority real, industria, profundidad técnica y cercanía con la trayectoria del candidato.
3. Si la vacante exige experiencia muy superior, conocimiento sectorial crítico o stack muy especializado, la afinidad debe bajar aunque haya skills parciales en común.
4. "encaje_estrategico" debe indicar si esta vacante acerca al candidato a su objetivo o lo desvía.
5. "decision_aplicacion":
   - "Aplicar sí o sí" = alta afinidad y probabilidad razonable de pasar filtros
   - "Aplicar si sobra tiempo" = afinidad media o brechas relevantes pero no fatales
   - "Descartar" = baja afinidad, seniority inalcanzable o desvío claro del objetivo
6. "ajustes_cv_recomendados" solo si afinidad es Alta o Media. Si es Baja, lista vacía [].
7. Sé directo y específico. No suavices el diagnóstico.
8. Los scores son auxiliares. El juicio cualitativo domina sobre el puntaje.
9. Scoring:
   - score_skills_tecnicas: % de skills requeridas que el candidato posee (0-100)
   - score_seniority: 100 si coincide, 60 si adyacente, 20 si muy distante
   - score_modalidad: 100 si compatible, 50 si no especificada, 0 si incompatible
   - score_idiomas: 100 si cumple o no se requieren, proporcional si cumple parcialmente
   - score_encaje_estrategico: 100 Alineado, 60 Parcialmente alineado, 20 Desvía
""".strip()


# ─────────────────────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────────────────────

PESOS = {
    'score_skills_tecnicas':    0.35,
    'score_seniority':          0.25,
    'score_idiomas':            0.10,
    'score_modalidad':          0.10,
    'score_encaje_estrategico': 0.20,
}


def _calcular_score_global(scores: dict) -> float:
    total = sum(scores.get(k, 0) * p for k, p in PESOS.items())
    return round(min(total, 100), 2)


def _calcular_semaforo(score: float) -> str:
    if score >= 70:
        return 'verde'
    if score >= 40:
        return 'amarillo'
    return 'rojo'


# ─────────────────────────────────────────────────────────────
# LLAMADAS A OPENAI
# ─────────────────────────────────────────────────────────────

def _llamar_openai(system: str, user: str) -> dict:
    """Llamada genérica a OpenAI. Retorna dict parseado o lanza excepción."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no esta configurada.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.2,
        max_tokens=2500,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def analizar_vacante(vacante: dict, perfil: dict) -> dict:
    """
    Analiza la afinidad entre una vacante y el perfil del usuario.
    Usa dos prompts separados: extracción y evaluación.

    Parámetros:
      vacante: dict con empresa, cargo, modalidad, descripcion
      perfil:  dict completo del usuario

    Retorna dict con success + todos los campos del análisis.
    """

    # ── PASO 1: Extracción ────────────────────────────────────
    user_extraccion = f"""
Empresa: {vacante.get('empresa', '')}
Cargo: {vacante.get('cargo', '')}
Modalidad declarada: {vacante.get('modalidad', 'No especificada')}

DESCRIPCIÓN DE LA VACANTE:
{vacante.get('descripcion', '')}
""".strip()

    try:
        extraccion = _llamar_openai(PROMPT_EXTRACCION, user_extraccion)
    except Exception as e:
        print(f"[ERROR] Extracción OpenAI: {e}")
        return {'success': False, 'message': f'Error en extracción: {str(e)}'}

    # ── PASO 2: Evaluación ────────────────────────────────────
    perfil_str   = json.dumps(perfil, ensure_ascii=False, indent=2)
    extraccion_str = json.dumps(extraccion, ensure_ascii=False, indent=2)

    user_evaluacion = f"""
PERFIL DEL CANDIDATO:
{perfil_str}

DATOS EXTRAÍDOS DE LA VACANTE:
{extraccion_str}

DESCRIPCIÓN ORIGINAL DE LA VACANTE:
Empresa: {vacante.get('empresa', '')}
Cargo: {vacante.get('cargo', '')}
{vacante.get('descripcion', '')}

Evalúa si esta vacante vale la pena para este candidato.
Actúa como reclutador senior y asesor de carrera.
Sé directo, específico y realista. No suavices el diagnóstico.
""".strip()

    try:
        evaluacion = _llamar_openai(PROMPT_EVALUACION, user_evaluacion)
    except Exception as e:
        print(f"[ERROR] Evaluación OpenAI: {e}")
        return {'success': False, 'message': f'Error en evaluación: {str(e)}'}

    # ── PASO 3: Consolidar resultado ──────────────────────────
    scores       = evaluacion.get('scores', {})
    score_global = _calcular_score_global(scores)
    semaforo     = _calcular_semaforo(score_global)

    return {
        'success': True,
        'message': '✓ Análisis completado',

        # Campos de extracción (Prompt 1)
        'tipo_real_de_rol':         extraccion.get('tipo_real_de_rol'),
        'seniority_inferido':       extraccion.get('seniority_inferido', 'No especificado'),
        'justificacion_seniority':  extraccion.get('justificacion_seniority'),
        'modalidad_detectada':      extraccion.get('modalidad_detectada'),
        'salario_detectado':        extraccion.get('salario_detectado'),
        'idiomas_requeridos':       extraccion.get('idiomas_requeridos', []),
        'skills_requeridas':        extraccion.get('skills_requeridas', []),
        'skills_blandas_detectadas': extraccion.get('skills_blandas_detectadas', []),

        # Campos de evaluación (Prompt 2)
        'afinidad_general':         evaluacion.get('afinidad_general', 'Baja'),
        'justificacion_afinidad':   evaluacion.get('justificacion_afinidad'),
        'fortalezas_principales':   evaluacion.get('fortalezas_principales', []),
        'riesgos_principales':      evaluacion.get('riesgos_principales', []),
        'skills_match':             evaluacion.get('skills_match', []),
        'skills_gap':               evaluacion.get('skills_gap', []),
        'encaje_estrategico':       evaluacion.get('encaje_estrategico'),
        'justificacion_encaje':     evaluacion.get('justificacion_encaje'),
        'decision_aplicacion':      evaluacion.get('decision_aplicacion'),
        'justificacion_decision':   evaluacion.get('justificacion_decision'),
        'ajustes_cv_recomendados':  evaluacion.get('ajustes_cv_recomendados', []),
        'aspiracion_salarial_sugerida': evaluacion.get('aspiracion_salarial_sugerida'),
        'resumen_analisis':         evaluacion.get('resumen_analisis'),

        # Scores
        'score_skills_tecnicas':    scores.get('score_skills_tecnicas', 0),
        'score_seniority':          scores.get('score_seniority', 0),
        'score_modalidad':          scores.get('score_modalidad', 0),
        'score_idiomas':            scores.get('score_idiomas', 0),
        'score_skills_blandas':     scores.get('score_encaje_estrategico', 0),
        'score_global':             score_global,
        'score_total':              score_global,  # compatibilidad con BD existente
        'semaforo':                 semaforo,
    }
