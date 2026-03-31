"""Application service that prepares profile data for AI vacancy analysis."""

from __future__ import annotations

from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository


class AnalysisService:
    """Coordinates profile aggregation for analysis workflows."""

    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    def build_profile_payload(self, perfil_id: int) -> dict | None:
        perfil = self.profile_repository.get_active_profile()
        if not perfil:
            return None

        skills = self.profile_repository.get_skills(perfil_id)
        experiencias = self.profile_repository.get_experiences(perfil_id)
        educacion = self.profile_repository.get_education(perfil_id)
        cursos = self.profile_repository.get_courses(perfil_id)
        certificaciones = self.profile_repository.get_certifications(perfil_id)

        def fmt(value):
            if not value:
                return None
            return value.strftime("%Y-%m") if hasattr(value, "strftime") else str(value)

        return {
            "nombre": perfil["nombre"],
            "titulo": perfil["titulo_profesional"],
            "nivel_actual": perfil["nivel_actual"],
            "anos_experiencia": perfil["anos_experiencia"],
            "salario_min": float(perfil["salario_min"]) if perfil.get("salario_min") else None,
            "salario_max": float(perfil["salario_max"]) if perfil.get("salario_max") else None,
            "moneda": perfil.get("moneda", "COP"),
            "modalidades_aceptadas": perfil.get("modalidades_aceptadas", ""),
            "skills": [
                {"categoria": skill["categoria"], "skill": skill["skill"], "nivel": skill["nivel"]}
                for skill in skills
            ],
            "experiencias": [
                {
                    "cargo": exp["cargo"],
                    "empresa": exp["empresa"],
                    "fecha_inicio": fmt(exp["fecha_inicio"]),
                    "fecha_fin": "Actualidad" if exp["es_trabajo_actual"] else fmt(exp["fecha_fin"]),
                    "funciones": exp["funciones"],
                    "logros": exp["logros"],
                }
                for exp in experiencias
            ],
            "educacion": [
                {
                    "titulo": item["titulo"],
                    "institucion": item["institucion"],
                    "nivel": item["nivel"],
                    "status": item["status"],
                }
                for item in educacion
            ],
            "cursos": [
                {"titulo": curso["titulo"], "institucion": curso["institucion"]}
                for curso in cursos
            ],
            "certificaciones": [
                {
                    "titulo": cert["titulo"],
                    "institucion": cert["institucion"],
                    "status": cert["status"],
                }
                for cert in certificaciones
            ],
        }
