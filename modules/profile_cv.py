"""CV view rendering extracted from the profile page."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def render_profile_cv_tab(perfil, perfil_id, database, fmt_fecha) -> None:
    """Render the read-only CV view for the profile tab."""
    if not perfil or not perfil_id:
        st.warning("⚠️ Completa tus **Datos Personales** para ver la Vista CV.")
        return

    skills = database.obtener_skills(perfil_id)
    experiencias = database.obtener_experiencias(perfil_id)
    educacion = database.obtener_educacion(perfil_id)
    cursos = database.obtener_cursos(perfil_id)
    certs = database.obtener_certificaciones(perfil_id)

    css = """
    <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Segoe UI', Calibri, sans-serif;
        color: #1a1a1a;
        background: #fff;
        padding: 24px 32px;
    }
    .cv-wrap { max-width: 820px; margin: 0 auto; }
    .cv-header    { text-align: center; margin-bottom: 8px; }
    .cv-name {
        font-size: 1.55rem; font-weight: 800;
        letter-spacing: 0.05em; text-transform: uppercase;
        color: #111; margin-bottom: 4px;
    }
    .cv-titulo {
        font-size: 0.72rem; font-weight: 600; color: #444;
        letter-spacing: 0.14em; text-transform: uppercase;
        margin-bottom: 5px;
    }
    .cv-tags   { font-size: 0.68rem; color: #666; margin-bottom: 5px; }
    .cv-contact { font-size: 0.68rem; color: #555; }
    .cv-contact a { color: #1a73e8; text-decoration: none; }
    .cv-hr     { border: none; border-top: 2px solid #111; margin: 10px 0 14px; }
    .cv-hr-thin { border: none; border-top: 1px solid #ccc; margin: 8px 0 12px; }
    .cv-sec-title {
        font-size: 0.68rem; font-weight: 800;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: #111; margin-bottom: 8px;
    }
    .cv-resumen { font-size: 0.78rem; line-height: 1.7; color: #333; }
    .cv-skill-row {
        display: flex; gap: 8px; align-items: baseline;
        margin-bottom: 3px; font-size: 0.75rem;
    }
    .cv-skill-cat { font-weight: 700; color: #111; min-width: 200px; flex-shrink: 0; }
    .cv-skill-lst { color: #333; }
    .cv-exp-hdr {
        display: flex; justify-content: space-between;
        align-items: baseline; margin-bottom: 1px;
    }
    .cv-exp-cargo {
        font-size: 0.78rem; font-weight: 700;
        text-transform: uppercase; color: #111;
    }
    .cv-exp-fecha { font-size: 0.68rem; color: #555; font-style: italic; }
    .cv-exp-emp { font-size: 0.74rem; color: #444; font-style: italic; margin-bottom: 5px; }
    .cv-bullet {
        font-size: 0.74rem; color: #333; line-height: 1.65;
        padding-left: 14px; text-indent: -8px; margin-bottom: 2px;
    }
    .cv-bullet::before { content: "• "; color: #111; }
    .cv-edu-row {
        display: flex; justify-content: space-between;
        font-size: 0.74rem; margin-bottom: 4px; gap: 8px;
    }
    .cv-edu-left { flex: 1; }
    .cv-edu-tit  { font-weight: 600; color: #111; }
    .cv-edu-inst { color: #555; font-style: italic; }
    .cv-edu-fecha { color: #666; white-space: nowrap; flex-shrink: 0; }
    .cv-subsec {
        font-size: 0.66rem; font-weight: 700; color: #555;
        letter-spacing: 0.1em; text-transform: uppercase;
        margin: 10px 0 5px;
    }
    .cv-exp-block { margin-bottom: 12px; }
    </style>
    """

    nombre = perfil.get("nombre", "").upper()
    titulo = perfil.get("titulo_profesional", "")
    tags = " • ".join([t.strip() for t in titulo.replace("|", "•").split("•") if t.strip()])

    contacto = []
    if perfil.get("correo"):
        contacto.append(perfil["correo"])
    if perfil.get("perfil_linkedin"):
        url = perfil["perfil_linkedin"]
        contacto.append(f"<a href='{url}' target='_blank'>{url}</a>")
    if perfil.get("ciudad"):
        contacto.append(perfil["ciudad"])
    if perfil.get("celular"):
        contacto.append(perfil["celular"])

    body = f"""
    <div class="cv-wrap">
      <div class="cv-header">
        <div class="cv-name">{nombre}</div>
        <div class="cv-titulo">{titulo}</div>
        <div class="cv-tags">{tags}</div>
        <div class="cv-contact">{' • '.join(contacto)}</div>
      </div>
      <hr class="cv-hr">
      <div class="cv-sec-title">Resumen Profesional</div>
      <div class="cv-resumen">{titulo}</div>
      <hr class="cv-hr-thin">
    """

    if skills:
        body += '<div class="cv-sec-title">Habilidades</div>'
        cats = {}
        for skill in skills:
            cats.setdefault(skill["categoria"], []).append(skill["skill"])
        for cat, lista in cats.items():
            body += f"""
            <div class="cv-skill-row">
                <span class="cv-skill-cat">{cat}:</span>
                <span class="cv-skill-lst">{' • '.join(lista)}</span>
            </div>"""
        body += '<hr class="cv-hr-thin">'

    if experiencias:
        body += '<div class="cv-sec-title">Experiencia Laboral</div>'
        for exp in experiencias:
            ff_str = "Actualidad" if exp["es_trabajo_actual"] else fmt_fecha(exp["fecha_fin"])
            fi_str = fmt_fecha(exp["fecha_inicio"])
            ciudad_str = f" | {exp['ciudad']}" if exp.get("ciudad") else ""
            body += f"""
            <div class="cv-exp-block">
              <div class="cv-exp-hdr">
                <span class="cv-exp-cargo">{exp['cargo']}</span>
                <span class="cv-exp-fecha">{fi_str} – {ff_str}</span>
              </div>
              <div class="cv-exp-emp">{exp['empresa']}{ciudad_str}</div>
            """
            for bloque in [exp.get("funciones"), exp.get("logros")]:
                if bloque:
                    for linea in bloque.split("\n"):
                        valor = linea.lstrip("•- ").strip()
                        if valor:
                            body += f'<div class="cv-bullet">{valor}</div>'
            body += "</div>"
        body += '<hr class="cv-hr-thin">'

    if educacion or certs or cursos:
        body += '<div class="cv-sec-title">Educación y Formación</div>'

        if educacion:
            body += '<div class="cv-subsec">Educación</div>'
            for item in educacion:
                fi = fmt_fecha(item["fecha_inicio"])
                ff = fmt_fecha(item["fecha_fin"]) if item["fecha_fin"] else item["status"]
                inst = item["institucion"]
                if item.get("ciudad"):
                    inst += f" | {item['ciudad']}"
                body += f"""
                <div class="cv-edu-row">
                  <div class="cv-edu-left">
                    <span class="cv-edu-tit">{item['titulo']}</span>
                    — <span class="cv-edu-inst">{inst}</span>
                  </div>
                  <div class="cv-edu-fecha">{fi} – {ff}</div>
                </div>"""

        if certs:
            body += '<div class="cv-subsec">Certificaciones</div>'
            for cert in certs:
                fo = fmt_fecha(cert["fecha_obtencion"])
                body += f"""
                <div class="cv-edu-row">
                  <div class="cv-edu-left">
                    <span class="cv-edu-tit">{cert['titulo']}</span>
                    — <span class="cv-edu-inst">{cert['institucion']}</span>
                  </div>
                  <div class="cv-edu-fecha">{fo} [{cert['status']}]</div>
                </div>"""

        if cursos:
            body += '<div class="cv-subsec">Cursos Relevantes</div>'
            body += '<div style="font-size:0.74rem;color:#333;line-height:1.8">'
            body += " • ".join([curso["titulo"] for curso in cursos])
            body += "</div>"

    body += "</div>"

    lineas_estimadas = (
        len(experiencias) * 120
        + len(skills) * 20
        + len(educacion) * 30
        + len(certs) * 25
        + len(cursos) * 15
        + 300
    )
    altura = max(600, min(lineas_estimadas, 3000))
    components.html(css + body, height=altura, scrolling=True)
