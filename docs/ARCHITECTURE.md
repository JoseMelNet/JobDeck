# Arquitectura

## Objetivo

El proyecto evoluciono de un MVP centrado en scripts a un monolito ordenado con capas claras.

## Capas

### Domain

Ubicacion: `app/domain`

Responsabilidades:

- enums de negocio
- excepciones de dominio

Regla:

- no depende de Streamlit, FastAPI ni `pyodbc`

### Application

Ubicacion: `app/application`

Responsabilidades:

- casos de uso
- orquestacion de flujos
- servicios de aplicacion como armado de payloads de analisis

Ejemplos:

- `CreateVacancyUseCase`
- `AnalyzeVacancyUseCase`
- `RegisterApplicationUseCase`

### Infrastructure

Ubicacion: `app/infrastructure`

Responsabilidades:

- conexion SQL Server
- repositorios
- persistencia de resultados de analisis

Ejemplos:

- `VacancyRepository`
- `ApplicationRepository`
- `ProfileRepository`
- `AnalysisRepository`

### Interfaces

Ubicacion practica actual:

- `app.py` y `modules/` para Streamlit
- `api.py` para FastAPI

Responsabilidades:

- recoger input
- llamar casos de uso o repositorios
- renderizar output

## Estado actual del refactor

Completado:

- eliminada la dependencia activa a `database.py`
- repositorios nativos sobre `pyodbc`
- casos de uso principales conectados
- particion de `mi_perfil.py`
- componentes UI reutilizables
- labels y estilos centralizados para UI
- tests unitarios y de API
- CI con sintaxis, lint y tests

Pendiente recomendado:

- adelgazar mas `modules/`
- mover mas logica de presentacion a componentes/presenters
- unificar mas validaciones de entrada
- ampliar cobertura de integracion real con BD si se necesita

## Configuracion de UI

### Navegacion principal

La aplicacion Streamlit se monta desde `app.py`.

La navegacion principal usa `st.tabs(...)` con cinco secciones:

1. `Registrar Vacante`
2. `Mis Vacantes`
3. `Registrar Aplicacion`
4. `Mis Aplicaciones`
5. `Mi Perfil`

Antes de renderizar las pestañas, `app.py` hace tres cosas:

- configura la pagina con `st.set_page_config(...)`
- valida conexion a SQL Server con `test_connection()`
- muestra metricas globales de vacantes y aplicaciones

Esto significa que la pantalla inicial funciona como dashboard liviano mas lanzador de modulos.

### Modulos de primer nivel

Cada pestaña principal delega el render a un modulo independiente en `modules/`:

- `modules/registrar_vacante.py`
- `modules/mis_vacantes.py`
- `modules/registrar_aplicacion.py`
- `modules/mis_aplicaciones.py`
- `modules/mi_perfil.py`

La idea actual es que estos modulos actuen como interfaz y orquestacion de pantalla, no como capa de persistencia.

### Estructura interna de Mi Perfil

`modules/mi_perfil.py` usa una segunda capa de `st.tabs(...)` para dividir el perfil en sub-secciones:

1. `Datos Personales`
2. `Skills`
3. `Experiencia`
4. `Proyectos`
5. `Educacion`
6. `Cursos`
7. `Certificaciones`
8. `Vista CV`

La implementacion esta partida en varios modulos:

- `modules/profile_tabs_primary.py`
  Maneja datos personales y skills.
- `modules/profile_tabs_background.py`
  Maneja experiencia, proyectos, educacion, cursos y certificaciones.
- `modules/profile_cv.py`
  Renderiza la vista resumida tipo CV.
- `modules/profile_shared.py`
  Centraliza utilidades compartidas de perfil.

Esta separacion reduce el tamano del modulo principal de perfil y facilita futuros cambios visuales por seccion.

### Patrones UI actuales

La UI actual usa tres patrones principales:

- tablas y filtros para vacantes
- tablero kanban para aplicaciones
- tabs internas para perfil

Adicionalmente hay dialogs, expanders, cards y bloques de metadata para detalle de registros.

### Componentes visuales compartidos

La carpeta `modules/components/` concentra la base visual reutilizable.

Piezas relevantes:

- `ui_styles.py`
  Inyecta estilos compartidos para management views.
- `ui_labels.py`
  Centraliza labels visibles, opciones y metadata de estados/modalidades.
- `profile_components.py`
  Componentes genericos para estados vacios, listas, metadata y acciones simples.
- `vacancy_components.py`
  Componentes especificos para resumen, analisis y acciones de vacantes.
- `application_components.py`
  Componentes especificos para tarjetas, columnas y detalle de aplicaciones.

### Estado de la UI

La UI ya esta mas ordenada que en la version original, pero todavia necesita una actualizacion visual completa.

Los puntos mas claros para una siguiente fase de rediseño son:

- unificar iconografia, textos y tono visual
- mejorar consistencia entre dashboard, vacantes, aplicaciones y perfil
- reducir HTML inline y mover mas presentacion a componentes dedicados
- convertir `app.py` en un shell visual mas limpio
- definir un sistema visual mas estable para cards, badges, filtros y acciones

## Flujo tipico

Vacantes:

1. Streamlit/FastAPI recibe datos
2. `CreateVacancyUseCase` valida y delega al repositorio
3. `AnalyzeVacancyUseCase` obtiene vacante, perfil y guarda analisis

Aplicaciones:

1. UI recoge datos
2. `RegisterApplicationUseCase` valida estado
3. `ApplicationRepository` persiste

Perfil:

1. Streamlit invoca `ProfileRepository`
2. `AnalysisService` compone payloads de perfil para analisis
