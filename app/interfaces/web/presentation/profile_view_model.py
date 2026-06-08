"""Functional presentation contract for the Perfil Laboral module."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProfileSectionId(str, Enum):
    SUMMARY = "summary"
    OBJECTIVE = "objective"
    SIGNALS = "signals"
    EVIDENCE = "evidence"
    CREDENTIALS = "credentials"
    OUTPUTS = "outputs"


class ProfileFieldUsage(str, Enum):
    VACANCY_ANALYSIS = "vacancy_analysis"
    BASE_CV = "base_cv"
    APPLICATION_MESSAGING = "application_messaging"
    SEARCH_STRATEGY = "search_strategy"
    OUTPUT_CONTACT = "output_contact"


class ProfileFieldPriority(str, Enum):
    CORE = "core"
    SUPPORTING = "supporting"
    SECONDARY = "secondary"


class ProfileDataConsumer(str, Enum):
    PROFILE_UI = "profile_ui"
    ANALYSIS_PAYLOAD = "analysis_payload"
    CV_PREVIEW = "cv_preview"


@dataclass(frozen=True)
class ProfileSectionDefinition:
    id: ProfileSectionId
    title: str
    summary: str


@dataclass(frozen=True)
class ProfileBlockDefinition:
    current_block_id: str
    current_label: str
    target_sections: tuple[ProfileSectionId, ...]
    target_goal: str
    current_consumers: tuple[ProfileDataConsumer, ...]
    notes: str


@dataclass(frozen=True)
class ProfileFieldDefinition:
    current_block_id: str
    field_id: str
    label: str
    target_section: ProfileSectionId
    target_usages: tuple[ProfileFieldUsage, ...]
    current_consumers: tuple[ProfileDataConsumer, ...]
    priority: ProfileFieldPriority
    notes: str = ""


@dataclass(frozen=True)
class ProfileLaborContract:
    sections: tuple[ProfileSectionDefinition, ...]
    blocks: tuple[ProfileBlockDefinition, ...]
    fields: tuple[ProfileFieldDefinition, ...]

    def fields_for_section(self, section_id: ProfileSectionId) -> tuple[ProfileFieldDefinition, ...]:
        return tuple(field for field in self.fields if field.target_section == section_id)

    def fields_for_usage(self, usage: ProfileFieldUsage) -> tuple[ProfileFieldDefinition, ...]:
        return tuple(field for field in self.fields if usage in field.target_usages)

    def field_by_key(self, block_id: str, field_id: str) -> ProfileFieldDefinition:
        return next(field for field in self.fields if field.current_block_id == block_id and field.field_id == field_id)


def _field(
    *,
    block_id: str,
    field_id: str,
    label: str,
    target_section: ProfileSectionId,
    target_usages: tuple[ProfileFieldUsage, ...],
    current_consumers: tuple[ProfileDataConsumer, ...],
    priority: ProfileFieldPriority,
    notes: str = "",
) -> ProfileFieldDefinition:
    return ProfileFieldDefinition(
        current_block_id=block_id,
        field_id=field_id,
        label=label,
        target_section=target_section,
        target_usages=target_usages,
        current_consumers=current_consumers,
        priority=priority,
        notes=notes,
    )


PROFILE_LABOR_SECTIONS = (
    ProfileSectionDefinition(
        id=ProfileSectionId.SUMMARY,
        title="Resumen",
        summary="Centro de control del perfil, cobertura y proxima accion.",
    ),
    ProfileSectionDefinition(
        id=ProfileSectionId.OBJECTIVE,
        title="Objetivo",
        summary="Preferencias y restricciones para decidir donde aplicar.",
    ),
    ProfileSectionDefinition(
        id=ProfileSectionId.SIGNALS,
        title="Senales",
        summary="Signals de matching para afinidad, brechas y estrategia.",
    ),
    ProfileSectionDefinition(
        id=ProfileSectionId.EVIDENCE,
        title="Evidencia",
        summary="Experiencia y proyectos que prueban capacidad real.",
    ),
    ProfileSectionDefinition(
        id=ProfileSectionId.CREDENTIALS,
        title="Credenciales",
        summary="Soporte formal del perfil, no centro del matching.",
    ),
    ProfileSectionDefinition(
        id=ProfileSectionId.OUTPUTS,
        title="Salidas",
        summary="Contacto, CV base y artefactos reutilizables de postulacion.",
    ),
)


PROFILE_LABOR_BLOCKS = (
    ProfileBlockDefinition(
        current_block_id="overview",
        current_label="Overview",
        target_sections=(ProfileSectionId.SUMMARY,),
        target_goal="Calidad del perfil, cobertura y siguiente accion.",
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        notes="Debe evolucionar de contadores a command center.",
    ),
    ProfileBlockDefinition(
        current_block_id="basics",
        current_label="Datos principales",
        target_sections=(ProfileSectionId.OBJECTIVE, ProfileSectionId.OUTPUTS),
        target_goal="Separar objetivo laboral de datos de salida y contacto.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Hoy mezcla matching, estrategia, contacto y salida.",
    ),
    ProfileBlockDefinition(
        current_block_id="skills",
        current_label="Skills",
        target_sections=(ProfileSectionId.SIGNALS, ProfileSectionId.SUMMARY),
        target_goal="Ser la base de afinidad, brechas y lenguaje reusable.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Es el bloque mas conectado al matching.",
    ),
    ProfileBlockDefinition(
        current_block_id="experiences",
        current_label="Experiencia",
        target_sections=(ProfileSectionId.EVIDENCE, ProfileSectionId.SUMMARY),
        target_goal="Respaldar matching, CV, mensajes e historias de impacto.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Ya sirve como evidencia principal.",
    ),
    ProfileBlockDefinition(
        current_block_id="projects",
        current_label="Proyectos",
        target_sections=(ProfileSectionId.EVIDENCE,),
        target_goal="Funcionar como evidencia reusable y no como isla separada.",
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        notes="Hoy no alimenta ni analisis ni vista CV.",
    ),
    ProfileBlockDefinition(
        current_block_id="education",
        current_label="Educacion",
        target_sections=(ProfileSectionId.CREDENTIALS,),
        target_goal="Respaldar el perfil sin competir con evidencia.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Debe mantenerse como soporte formal.",
    ),
    ProfileBlockDefinition(
        current_block_id="courses",
        current_label="Cursos",
        target_sections=(ProfileSectionId.CREDENTIALS,),
        target_goal="Reforzar el perfil, no dominar la pantalla.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Aporta soporte puntual al matching.",
    ),
    ProfileBlockDefinition(
        current_block_id="certifications",
        current_label="Certificaciones",
        target_sections=(ProfileSectionId.CREDENTIALS,),
        target_goal="Aportar soporte verificable del perfil.",
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        notes="Debe convivir con cursos como refuerzo.",
    ),
    ProfileBlockDefinition(
        current_block_id="profile_status",
        current_label="Estado del perfil",
        target_sections=(ProfileSectionId.SUMMARY,),
        target_goal="Mostrar calidad y accion recomendada, no detalles internos.",
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        notes="Debe dejar de exponer estados internos como migracion.",
    ),
    ProfileBlockDefinition(
        current_block_id="cv_preview",
        current_label="Vista CV",
        target_sections=(ProfileSectionId.OUTPUTS,),
        target_goal="Consolidar salidas reutilizables del perfil.",
        current_consumers=(ProfileDataConsumer.CV_PREVIEW,),
        notes="Hoy depende parcialmente de composicion en Python.",
    ),
)


PROFILE_LABOR_FIELDS = (
    _field(
        block_id="basics",
        field_id="nombre",
        label="Nombre completo",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
        notes="Identidad de salida; hoy aparece tambien en el payload de analisis.",
    ),
    _field(
        block_id="basics",
        field_id="titulo_profesional",
        label="Titulo profesional",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(
            ProfileFieldUsage.VACANCY_ANALYSIS,
            ProfileFieldUsage.BASE_CV,
            ProfileFieldUsage.APPLICATION_MESSAGING,
            ProfileFieldUsage.SEARCH_STRATEGY,
        ),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="ciudad",
        label="Ciudad",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.SEARCH_STRATEGY, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SUPPORTING,
        notes="Ubicacion estrategica y de salida.",
    ),
    _field(
        block_id="basics",
        field_id="direccion",
        label="Direccion",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.OUTPUT_CONTACT,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
        notes="Dato de salida secundario y candidato a ocultarse.",
    ),
    _field(
        block_id="basics",
        field_id="celular",
        label="Celular",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="correo",
        label="Correo",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="perfil_linkedin",
        label="Perfil LinkedIn",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="basics",
        field_id="perfil_github",
        label="Perfil GitHub",
        target_section=ProfileSectionId.OUTPUTS,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
        notes="Hoy no se refleja en analisis ni vista CV.",
    ),
    _field(
        block_id="basics",
        field_id="nivel_actual",
        label="Nivel actual",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="anos_experiencia",
        label="Anios de experiencia",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="salario_min",
        label="Salario minimo",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="salario_max",
        label="Salario maximo",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="basics",
        field_id="moneda",
        label="Moneda",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="basics",
        field_id="modalidades_aceptadas",
        label="Modalidades aceptadas",
        target_section=ProfileSectionId.OBJECTIVE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="skills",
        field_id="categoria",
        label="Categoria de skill",
        target_section=ProfileSectionId.SIGNALS,
        target_usages=(
            ProfileFieldUsage.VACANCY_ANALYSIS,
            ProfileFieldUsage.BASE_CV,
            ProfileFieldUsage.APPLICATION_MESSAGING,
            ProfileFieldUsage.SEARCH_STRATEGY,
        ),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="skills",
        field_id="skill",
        label="Skill",
        target_section=ProfileSectionId.SIGNALS,
        target_usages=(
            ProfileFieldUsage.VACANCY_ANALYSIS,
            ProfileFieldUsage.BASE_CV,
            ProfileFieldUsage.APPLICATION_MESSAGING,
            ProfileFieldUsage.SEARCH_STRATEGY,
        ),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="skills",
        field_id="nivel",
        label="Nivel de skill",
        target_section=ProfileSectionId.SIGNALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="experiences",
        field_id="cargo",
        label="Cargo",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(
            ProfileFieldUsage.VACANCY_ANALYSIS,
            ProfileFieldUsage.BASE_CV,
            ProfileFieldUsage.APPLICATION_MESSAGING,
            ProfileFieldUsage.SEARCH_STRATEGY,
        ),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="experiences",
        field_id="empresa",
        label="Empresa",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="experiences",
        field_id="ciudad",
        label="Ciudad de experiencia",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="experiences",
        field_id="descripcion_empresa",
        label="Descripcion de empresa",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
        notes="Contexto util pero no signal de matching.",
    ),
    _field(
        block_id="experiences",
        field_id="fecha_inicio",
        label="Fecha de inicio",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="experiences",
        field_id="fecha_fin",
        label="Fecha de fin",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="experiences",
        field_id="es_trabajo_actual",
        label="Trabajo actual",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="experiences",
        field_id="funciones",
        label="Funciones",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="experiences",
        field_id="logros",
        label="Logros",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="projects",
        field_id="nombre",
        label="Nombre de proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.CORE,
        notes="Debe vivir como evidencia y no como isla separada.",
    ),
    _field(
        block_id="projects",
        field_id="empresa",
        label="Empresa del proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="projects",
        field_id="ciudad",
        label="Ciudad del proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="projects",
        field_id="fecha_inicio",
        label="Fecha de inicio de proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="projects",
        field_id="fecha_fin",
        label="Fecha de fin de proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="projects",
        field_id="es_proyecto_actual",
        label="Proyecto en curso",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="projects",
        field_id="stack",
        label="Stack del proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="projects",
        field_id="funciones",
        label="Descripcion del proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="projects",
        field_id="logros",
        label="Logros del proyecto",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.CORE,
    ),
    _field(
        block_id="projects",
        field_id="url_repositorio",
        label="URL de repositorio",
        target_section=ProfileSectionId.EVIDENCE,
        target_usages=(ProfileFieldUsage.BASE_CV, ProfileFieldUsage.APPLICATION_MESSAGING, ProfileFieldUsage.OUTPUT_CONTACT),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="education",
        field_id="titulo",
        label="Titulo academico",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="education",
        field_id="institucion",
        label="Institucion educativa",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="education",
        field_id="ciudad",
        label="Ciudad de educacion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="education",
        field_id="nivel",
        label="Nivel educativo",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="education",
        field_id="fecha_inicio",
        label="Fecha de inicio de educacion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="education",
        field_id="fecha_fin",
        label="Fecha de fin de educacion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="education",
        field_id="status",
        label="Estado educativo",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="courses",
        field_id="titulo",
        label="Titulo de curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="courses",
        field_id="institucion",
        label="Institucion del curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.ANALYSIS_PAYLOAD),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="courses",
        field_id="fecha_inicio",
        label="Fecha de inicio del curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="courses",
        field_id="fecha_fin",
        label="Fecha de fin del curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="courses",
        field_id="status",
        label="Estado del curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.SEARCH_STRATEGY,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="courses",
        field_id="url_certificado",
        label="URL del certificado del curso",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.OUTPUT_CONTACT,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
        notes="Soporte verificable, no signal principal.",
    ),
    _field(
        block_id="certifications",
        field_id="titulo",
        label="Titulo de certificacion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="certifications",
        field_id="institucion",
        label="Institucion certificadora",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="certifications",
        field_id="fecha_obtencion",
        label="Fecha de obtencion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.BASE_CV,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI, ProfileDataConsumer.CV_PREVIEW),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="certifications",
        field_id="fecha_vencimiento",
        label="Fecha de vencimiento",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.SEARCH_STRATEGY,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
    _field(
        block_id="certifications",
        field_id="status",
        label="Estado de certificacion",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.VACANCY_ANALYSIS, ProfileFieldUsage.BASE_CV, ProfileFieldUsage.SEARCH_STRATEGY),
        current_consumers=(
            ProfileDataConsumer.PROFILE_UI,
            ProfileDataConsumer.ANALYSIS_PAYLOAD,
            ProfileDataConsumer.CV_PREVIEW,
        ),
        priority=ProfileFieldPriority.SUPPORTING,
    ),
    _field(
        block_id="certifications",
        field_id="url_certificado",
        label="URL del certificado",
        target_section=ProfileSectionId.CREDENTIALS,
        target_usages=(ProfileFieldUsage.OUTPUT_CONTACT,),
        current_consumers=(ProfileDataConsumer.PROFILE_UI,),
        priority=ProfileFieldPriority.SECONDARY,
    ),
)


def build_profile_labor_contract() -> ProfileLaborContract:
    return ProfileLaborContract(
        sections=PROFILE_LABOR_SECTIONS,
        blocks=PROFILE_LABOR_BLOCKS,
        fields=PROFILE_LABOR_FIELDS,
    )


__all__ = [
    "PROFILE_LABOR_BLOCKS",
    "PROFILE_LABOR_FIELDS",
    "PROFILE_LABOR_SECTIONS",
    "ProfileBlockDefinition",
    "ProfileDataConsumer",
    "ProfileFieldDefinition",
    "ProfileFieldPriority",
    "ProfileFieldUsage",
    "ProfileLaborContract",
    "ProfileSectionDefinition",
    "ProfileSectionId",
    "build_profile_labor_contract",
]
