# CVs-Optimizator

Aplicacion para registrar vacantes, analizarlas contra un perfil profesional y gestionar aplicaciones laborales.

## Estado actual

- Streamlit como interfaz principal en `app.py`
- FastAPI para integraciones locales en `api.py`
- arquitectura por capas en `app/`
- persistencia SQL Server via `pyodbc`
- suite automatizada con `unittest`
- CI en GitHub Actions con sintaxis, lint y tests

## Funcionalidades

- registrar vacantes
- listar, archivar, reactivar y eliminar vacantes
- analizar vacantes contra el perfil activo
- registrar y gestionar aplicaciones
- tablero de aplicaciones por estado
- gestionar perfil profesional, skills, experiencia, proyectos, educacion, cursos y certificaciones

## Estructura

```text
CVs-Optimizator/
├── app.py
├── api.py
├── app/
│   ├── application/
│   ├── config/
│   ├── domain/
│   └── infrastructure/
├── modules/
│   ├── components/
│   ├── registrar_vacante.py
│   ├── mis_vacantes.py
│   ├── registrar_aplicacion.py
│   ├── mis_aplicaciones.py
│   └── mi_perfil.py
├── tests/
├── sql_queries/
├── run_tests.py
└── .github/workflows/ci.yml
```

## Requisitos

- Windows
- Python 3.11 recomendado
- SQL Server accesible desde `pyodbc`
- variables de entorno para BD

## Configuracion

1. Crea `.env` a partir de `.env.example`.
2. Ajusta credenciales de SQL Server.

Variables usadas:

```env
DB_SERVER=localhost\MSSQLSERVER2025
DB_DATABASE=job_postings_mvp
DB_USER=sa
DB_PASSWORD=tu_password
```

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion

Streamlit:

```bash
streamlit run app.py
```

API local:

```bash
uvicorn api:app --reload
```

Prueba rapida de BD:

```bash
python test_connection.py
```

## Tests

Entrada unica recomendada:

```bash
python run_tests.py
```

Estado actual de la suite:

- tests de UI compartida
- tests de casos de uso
- tests de repositorios
- tests de API
- tests de flujos integrados con mocks

## CI

Workflow disponible en `.github/workflows/ci.yml`.

Ejecuta:

- `compileall`
- `ruff check`
- `python run_tests.py`

## Arquitectura

Resumen corto:

- `app/domain`: enums y excepciones
- `app/application`: casos de uso y servicios
- `app/infrastructure`: conexion y repositorios
- `modules`: interfaces Streamlit y componentes visuales

Detalle adicional en [docs/ARCHITECTURE.md](/C:/Users/josem/PycharmProjects/CVs-Optimizator/docs/ARCHITECTURE.md).

## UI actual

La interfaz principal esta montada en `app.py` con `st.tabs(...)` como mecanismo de navegacion horizontal.

Pestanas principales:

- `Registrar Vacante`: formulario de alta de vacantes
- `Mis Vacantes`: tabla filtrable, detalle y acciones sobre vacantes
- `Registrar Aplicacion`: formulario de registro de aplicaciones
- `Mis Aplicaciones`: tablero kanban por estado y dialogo de detalle
- `Mi Perfil`: gestion completa del perfil profesional

La pestana `Mi Perfil` tiene una segunda capa de navegacion interna:

- `Datos Personales`
- `Skills`
- `Experiencia`
- `Proyectos`
- `Educacion`
- `Cursos`
- `Certificaciones`
- `Vista CV`

Ademas, la UI comparte componentes visuales en `modules/components/` para evitar duplicacion entre pantallas. Ahi viven estilos comunes, labels centralizados y componentes especificos para vacantes, aplicaciones y secciones de perfil.

## Notas

- el proyecto fue migrado desde una estructura mas monolitica a una arquitectura por capas
- la suite actual corre localmente con `43` tests
- el pipeline de CI ya esta preparado para validar cambios automaticamente
