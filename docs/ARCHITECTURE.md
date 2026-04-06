# Arquitectura

## Objetivo

El proyecto evoluciono de un MVP centrado en scripts a un monolito ordenado con capas claras y con interfaz principal web.

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

- [api.py](/C:/Users/josem/PycharmProjects/CVs-Optimizator/api.py) como entrada HTTP
- `app/interfaces/web/` como interfaz principal HTML

Responsabilidades:

- recoger input
- llamar casos de uso o repositorios
- renderizar output

## Estado actual del refactor

Completado:

- eliminada la dependencia activa a `database.py`
- repositorios nativos sobre `pyodbc`
- casos de uso principales conectados
- interfaz web principal sobre FastAPI + Jinja2 + HTMX
- `Mi Perfil` migrado a web, incluida `Vista CV`
- tests unitarios y de API
- tests de rutas web principales
- CI con sintaxis, lint y tests

Pendiente recomendado:

- seguir puliendo UX y consistencia visual de la interfaz web
- ampliar cobertura de integracion real con BD si se necesita

## Configuracion de UI

### Interfaz principal web

La aplicacion principal ahora vive en [api.py](/C:/Users/josem/PycharmProjects/CVs-Optimizator/api.py) y monta la interfaz HTML desde `app/interfaces/web/`.

Ruta principal:

- `/app`

Tecnologia usada:

- FastAPI
- Jinja2
- HTMX
- CSS propio

### Navegacion principal web

La interfaz web sigue el flujo real de trabajo:

1. `Nueva Vacante`
2. `Inbox`
3. `Seguimiento`
4. `Mi Perfil`

Esto alinea la UI con el uso real:

- entra vacante
- se analiza
- se revisa en inbox
- si interesa, pasa a seguimiento
- el perfil se mantiene aparte como contexto para analisis

### Mi Perfil web

`Mi Perfil` ya cubre de forma operativa:

- datos principales
- skills
- experiencia
- proyectos
- educacion
- cursos
- certificaciones
- vista CV

Patrones usados:

- formularios HTML simples
- refresco parcial con HTMX
- tarjetas expandibles para experiencia y proyectos
- bloques de resumen y ayuda
- vista CV de solo lectura generada desde el mismo perfil
- paginacion para listas largas con tamano de pagina configurable

`app.py` en la raiz queda solo como acceso rapido informativo para abrir la interfaz web.

## Flujo tipico

Vacantes:

1. la web o la extension registran la vacante
2. `CreateVacancyUseCase` valida y delega al repositorio
3. `AnalyzeVacancyUseCase` obtiene vacante, perfil y guarda analisis
4. la vacante se revisa en `Inbox`

Aplicaciones:

1. desde `Inbox`, la vacante pasa a seguimiento
2. `RegisterApplicationUseCase` crea la aplicacion en estado inicial
3. `Seguimiento` permite actualizar el estado real del proceso

Perfil:

1. la web invoca `ProfileRepository`
2. el perfil se mantiene desde formularios HTML
3. `AnalysisService` compone payloads de perfil para analisis
4. la `Vista CV` resume el perfil consolidado
