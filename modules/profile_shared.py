"""Shared helpers and constants for the profile Streamlit modules."""

from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository


class ProfileDatabaseAdapter:
    """Compatibility adapter to keep the current profile UI over the repository layer."""

    def __init__(self, repository: ProfileRepository) -> None:
        self.repository = repository

    def obtener_perfil(self):
        return self.repository.get_active_profile()

    def guardar_perfil(self, datos):
        return self.repository.save_profile(datos)

    def obtener_skills(self, perfil_id):
        return self.repository.get_skills(perfil_id)

    def insertar_skill(self, perfil_id, categoria, skill, nivel):
        return self.repository.add_skill(perfil_id, categoria, skill, nivel)

    def eliminar_skill(self, skill_id):
        return self.repository.delete_skill(skill_id)

    def obtener_experiencias(self, perfil_id):
        return self.repository.get_experiences(perfil_id)

    def insertar_experiencia(self, perfil_id, datos):
        return self.repository.add_experience(perfil_id, datos)

    def eliminar_experiencia(self, exp_id):
        return self.repository.delete_experience(exp_id)

    def actualizar_experiencia(self, exp_id, datos):
        return self.repository.update_experience(exp_id, datos)

    def obtener_proyectos(self, perfil_id):
        return self.repository.get_projects(perfil_id)

    def insertar_proyecto(self, perfil_id, datos):
        return self.repository.add_project(perfil_id, datos)

    def eliminar_proyecto(self, proyecto_id):
        return self.repository.delete_project(proyecto_id)

    def obtener_educacion(self, perfil_id):
        return self.repository.get_education(perfil_id)

    def insertar_educacion(self, perfil_id, datos):
        return self.repository.add_education(perfil_id, datos)

    def eliminar_educacion(self, edu_id):
        return self.repository.delete_education(edu_id)

    def obtener_cursos(self, perfil_id):
        return self.repository.get_courses(perfil_id)

    def insertar_curso(self, perfil_id, datos):
        return self.repository.add_course(perfil_id, datos)

    def eliminar_curso(self, curso_id):
        return self.repository.delete_course(curso_id)

    def obtener_certificaciones(self, perfil_id):
        return self.repository.get_certifications(perfil_id)

    def insertar_certificacion(self, perfil_id, datos):
        return self.repository.add_certification(perfil_id, datos)

    def eliminar_certificacion(self, cert_id):
        return self.repository.delete_certification(cert_id)


database = ProfileDatabaseAdapter(ProfileRepository())

NIVELES_SENIORITY = ["Junior", "Mid", "Senior"]
CATEGORIAS_SKILL_DEFAULT = [
    "Bases de Datos",
    "Lenguajes de Programación",
    "Visualización",
    "Cloud",
    "ETL / Integración",
    "Herramientas",
    "Metodologías",
    "Blandas",
    "Idiomas",
    "Otra",
]
NIVELES_SKILL_TECNICO = ["Básico", "Intermedio", "Avanzado", "Experto"]
NIVELES_IDIOMA = ["A1", "A2", "B1", "B2", "C1", "C2", "Nativo"]
NIVELES_EDUCACION = [
    "Bachillerato",
    "Técnico",
    "Tecnólogo",
    "Pregrado",
    "Especialización",
    "Maestría",
    "Doctorado",
    "Otro",
]
STATUS_EDUCACION = ["En curso", "Completado", "Pausado", "Abandonado"]
STATUS_CURSOS = ["En curso", "Completado", "Pausado"]
STATUS_CERT = ["Vigente", "Vencido", "En proceso"]
MODALIDADES = ["Remoto", "Presencial", "Híbrido"]
MONEDAS = ["COP", "USD", "EUR", "MXN", "ARS"]


def fmt_fecha(fecha) -> str:
    if not fecha:
        return "—"
    if isinstance(fecha, (datetime, date)):
        return fecha.strftime("%m/%Y")
    return str(fecha)


def get_categorias() -> list:
    if "skills_categorias_custom" not in st.session_state:
        st.session_state.skills_categorias_custom = []
    return CATEGORIAS_SKILL_DEFAULT + [
        value for value in st.session_state.skills_categorias_custom if value not in CATEGORIAS_SKILL_DEFAULT
    ]
