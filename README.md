# CVs-Optimizator

Aplicacion para registrar vacantes, analizarlas contra un perfil profesional y gestionar aplicaciones laborales.

## Estado actual

- interfaz principal web sobre `FastAPI + Jinja2 + HTMX`
- arquitectura por capas en `app/`
- persistencia SQL Server via `pyodbc`
- suite automatizada con `unittest`
- CI en GitHub Actions con sintaxis, lint y tests

## Funcionalidades

- registrar vacantes
- listar, archivar, reactivar y eliminar vacantes
- analizar vacantes contra el perfil activo
- gestionar aplicaciones y su seguimiento
- gestionar perfil profesional, skills, experiencia, proyectos, educacion, cursos y certificaciones
- renderizar una vista CV consolidada desde la web

## Estructura

```text
CVs-Optimizator/
|-- app.py
|-- api.py
|-- app/
|   |-- application/
|   |-- config/
|   |-- domain/
|   |-- infrastructure/
|   `-- interfaces/
|       `-- web/
|-- modules/
|-- tests/
|-- sql_queries/
|-- run_tests.py
`-- .github/workflows/ci.yml
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

Interfaz principal web:

```bash
uvicorn api:app --reload
```

Luego abre:

```text
http://127.0.0.1:8000/app
```

Prueba rapida de BD:

```bash
python test_connection.py
```

## Flujo principal de la web

1. `Nueva Vacante`
2. `Inbox`
3. `Seguimiento`
4. `Mi Perfil`

La interfaz web ya cubre el flujo principal del producto:

- registrar vacante
- analizarla
- revisarla en inbox
- moverla a seguimiento
- actualizar estados de aplicacion
- mantener perfil y vista CV

Las vistas largas de `Inbox` y `Seguimiento` ya incluyen paginacion y tamano de pagina configurable para evitar listas demasiado pesadas.

## Tests

Entrada unica recomendada:

```bash
python run_tests.py
```

Estado actual de la suite principal:

- tests de casos de uso
- tests de repositorios
- tests de API
- tests de rutas web
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
- `app/interfaces/web`: interfaz HTML principal
- `modules`: codigo residual compartido, como `analizar_vacante.py`

Detalle adicional en [ARCHITECTURE.md](/C:/Users/josem/PycharmProjects/CVs-Optimizator/docs/ARCHITECTURE.md).

## Notas

- la web es ahora la interfaz recomendada
- `app.py` en la raiz queda solo como acceso rapido informativo
- la suite principal corre localmente con `53` tests cubriendo la interfaz web principal
- el pipeline de CI ya esta preparado para validar cambios automaticamente
