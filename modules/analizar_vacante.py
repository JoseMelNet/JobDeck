"""
modules/analizar_vacante.py
Motor de análisis de afinidad vacante vs perfil usando OpenAI.

Se llama desde mis_vacantes.py:
    from modules.analizar_vacante import analizar_vacante
    resultado = analizar_vacante(vacante_dict, perfil_dict)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# ─────────────────────────────────────────────────────────────
# CLIENTE OPENAI
# ─────────────────────────────────────────────────────────────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODELO = "gpt-4o-mini"


# ─────────────────────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
Eres un experto en reclutamiento de tecnología y análisis de perfiles profesionales.
Tu tarea es analizar la compatibilidad entre un perfil profesional y una vacante laboral.

Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin markdown,
sin bloques de código. Solo el JSON puro.

El JSON debe tener exactamente esta estructura:
{
  "skills_requeridas": [
    {"skill": "nombre", "tipo": "requerido|deseable"}
  ],
  "skills_blandas_detectadas": ["skill1", "skill2"],
  "seniority_inferido": "Junior|Mid|Senior|No especificado",
  "justificacion_seniority": "Texto explicando por qué se infirió ese nivel",
  "modalidad_detectada": "Remoto|Presencial|Híbrido|No especificado",
  "salario_detectado": "texto con el salario o null si no se menciona",
  "idiomas_requeridos": [
    {"idioma": "nombre", "nivel": "nivel requerido"}
  ],
  "score_skills_tecnicas": número entre 0 y 100,
  "score_seniority": número entre 0 y 100,
  "score_modalidad": número entre 0 y 100,
  "score_idiomas": número entre 0 y 100,
  "score_skills_blandas": número entre 0 y 100,
  "skills_match": ["skill1", "skill2"],
  "skills_gap": ["skill1", "skill2"],
  "resumen_analisis": "Párrafo de 3-5 líneas con el análisis general",
  "aspiracion_salarial_sugerida": "rango sugerido o null"
}

Reglas para el scoring:
- score_skills_tecnicas (40%): porcentaje de skills requeridas que el candidato posee
- score_seniority (20%): 100 si el nivel coincide exactamente, 60 si es adyacente, 20 si hay gran diferencia
- score_modalidad (15%): 100 si la modalidad de la vacante está entre las aceptadas por el candidato, 0 si no
- score_idiomas (10%): 100 si cumple todos los requisitos, 50 si cumple parcialmente, 100 si no se requieren idiomas
- score_skills_blandas (15%): porcentaje de skills blandas detectadas que el candidato tiene registradas

Sé preciso y objetivo. El resumen_analisis debe mencionar: nivel inferido con justificación,
skills más relevantes que tiene el candidato, principales gaps, y observación sobre salario si aplica.
""".strip()


# ─────────────────────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────────────────────

PESOS = {
    'score_skills_tecnicas': 0.40,
    'score_seniority':       0.20,
    'score_modalidad':       0.15,
    'score_idiomas':         0.10,
    'score_skills_blandas':  0.15,
}


def _score_total(r: dict) -> float:
    total = sum(r.get(k, 0) * p for k, p in PESOS.items())
    return round(min(total, 100), 2)


def _semaforo(score: float) -> str:
    if score >= 70:   return 'verde'
    elif score >= 40: return 'amarillo'
    else:             return 'rojo'


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def analizar_vacante(vacante: dict, perfil: dict) -> dict:
    """
    Analiza la afinidad entre una vacante y el perfil del usuario.

    Parámetros:
      vacante: dict con empresa, cargo, modalidad, descripcion
      perfil:  dict completo del usuario (de obtener_perfil_completo_para_analisis)

    Retorna dict con success, message y todos los campos del análisis.
    """
    prompt_usuario = f"""
## PERFIL DEL CANDIDATO
{json.dumps(perfil, ensure_ascii=False, indent=2)}

## DESCRIPCIÓN DE LA VACANTE
Empresa: {vacante.get('empresa', '')}
Cargo: {vacante.get('cargo', '')}
Modalidad declarada: {vacante.get('modalidad', '')}

{vacante.get('descripcion', '')}

Analiza la compatibilidad y responde con el JSON estructurado.
""".strip()

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt_usuario},
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)

        # Calcular score total y semáforo
        score_total = _score_total(data)
        semaforo    = _semaforo(score_total)

        return {
            'success':                    True,
            'message':                    '✓ Análisis completado',
            'skills_requeridas':          data.get('skills_requeridas', []),
            'skills_blandas_detectadas':  data.get('skills_blandas_detectadas', []),
            'seniority_inferido':         data.get('seniority_inferido', 'No especificado'),
            'justificacion_seniority':    data.get('justificacion_seniority'),
            'modalidad_detectada':        data.get('modalidad_detectada'),
            'salario_detectado':          data.get('salario_detectado'),
            'idiomas_requeridos':         data.get('idiomas_requeridos', []),
            'skills_match':               data.get('skills_match', []),
            'skills_gap':                 data.get('skills_gap', []),
            'resumen_analisis':           data.get('resumen_analisis'),
            'aspiracion_salarial_sugerida': data.get('aspiracion_salarial_sugerida'),
            'score_total':                score_total,
            'score_skills_tecnicas':      data.get('score_skills_tecnicas', 0),
            'score_seniority':            data.get('score_seniority', 0),
            'score_modalidad':            data.get('score_modalidad', 0),
            'score_idiomas':              data.get('score_idiomas', 0),
            'score_skills_blandas':       data.get('score_skills_blandas', 0),
            'semaforo':                   semaforo,
        }

    except json.JSONDecodeError as e:
        print(f"[ERROR] analizar_vacante JSON: {e}")
        return {'success': False, 'message': f'Error al parsear respuesta de OpenAI: {str(e)}'}
    except Exception as e:
        print(f"[ERROR] analizar_vacante: {e}")
        return {'success': False, 'message': f'Error al llamar a OpenAI: {str(e)}'}