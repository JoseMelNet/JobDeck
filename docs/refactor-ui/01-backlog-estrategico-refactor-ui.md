# Backlog estrategico - Refactor UI Job-Deck

## 1. Proposito

Este documento define la ruta estrategica para actualizar el frontend de Job-Deck de forma incremental, controlada y reversible, sin una reescritura total inicial.

Su funcion es servir como backlog maestro por fases para guiar el refactor UI sobre la base actual de FastAPI + Jinja2 + HTMX, protegiendo los flujos ya estabilizados y separando esta tarea documental de la ejecucion tecnica posterior.

Este documento se crea y se versiona directamente en `main` como punto de partida. El refactor UI real no debe ejecutarse en `main`; debe continuar en una rama dedicada creada despues de este commit documental.

## 2. Estado actual resumido

### Stack actual

- FastAPI
- Jinja2
- HTMX
- SQL Server via `pyodbc`
- OpenAI para analisis de vacantes
- Extension Chrome para captura de vacantes desde LinkedIn

### Pantallas principales

- Dashboard web existente, pero no usado como entrypoint principal
- Inbox de vacantes
- Detalle de vacante integrado en Inbox
- Nueva vacante
- Seguimiento de aplicaciones
- Perfil profesional
- Partials HTMX para Inbox, Seguimiento y Perfil

### Fortalezas actuales

- No hay razon tecnica fuerte para migrar ahora a React, Vue o Next.
- La base FastAPI + Jinja2 + HTMX ya resuelve navegacion, filtros, paginacion y formularios operativos.
- `base.html` ya funciona como layout principal compartido.
- Inbox ya esta orientado a decision rapida.
- Existen patrones visuales rescatables: badges, pills, KPI strips, empty states.
- El uso de JavaScript custom es minimo.
- `main` esta estabilizado con `68 tests OK`, `ruff OK` y `compileall OK`.

### Problemas estructurales detectados en FRONT-0

- CSS monolitico y con mezcla de estilos globales, componentes y estilos de pantalla.
- Duplicacion visual entre Vacancies y Applications.
- Granularidad HTMX inconsistente entre pantallas.
- Endpoints parciales residuales o no alineados con los flujos vivos.
- `Profile` demasiado acoplado y con re-render amplio.
- `Vacancies` y `Applications` tienen patrones parecidos, pero no uniformes.
- La cobertura web actual es util, pero limitada para partials HTMX y riesgos de regresion visual-estructural.

### Riesgos principales

- Romper seleccion y paginacion en Inbox.
- Romper `hx-target`, `hx-swap` o `hx-push-url`.
- Degradar `Profile` por re-render completo.
- Limpiar CSS sin identificar antes que clases siguen vivas.
- Afectar indirectamente la captura desde la extension Chrome.

## 3. Decisiones tecnicas iniciales

- Se conserva `Jinja2 + HTMX` como base inicial del refactor.
- No se migra a `React`, `Vue` o `Next` por ahora.
- No se reescribe todo el frontend de golpe.
- Se prioriza evolucion incremental sobre la interfaz actual.
- Se protege la captura desde `chrome-extension/` y sus contratos actuales.
- Se protege Inbox como flujo principal de decision operativa.
- Se evita redisenar `Profile` demasiado pronto; primero se reduce acoplamiento.
- Todo cambio operativo del refactor UI debe hacerse fuera de `main`, en una rama dedicada creada despues de este documento.

## 4. Principios del refactor UI

- Cambios pequenos, reversibles y con alcance claro.
- Mantener equivalencia funcional mientras se ordena la estructura.
- No romper rutas ni contratos HTMX sin una necesidad concreta.
- Primero estructura y consistencia; despues ajustes visuales mayores.
- Primero componentes compartidos y deuda de base; despues pantallas complejas.
- Tests antes o junto con cambios riesgosos.
- Cada fase debe cerrar con validaciones proporcionales a su riesgo.
- El refactor debe mejorar mantenibilidad sin frenar el flujo diario de uso.

## 5. Fases estrategicas del refactor

### FRONT-1 - Preparar rama unica del refactor UI

- Objetivo: crear una rama dedicada para todo el refactor UI a partir de `main` actualizado, despues de este commit documental.
- Alcance general:
  - verificar `main` limpio y sincronizado;
  - crear la rama sugerida `frontend/refactor-ui`;
  - confirmar estado inicial read-only antes de tocar frontend.
- Riesgo: bajo.
- Criterio de cierre:
  - existe una rama dedicada para el refactor UI;
  - queda explicitado que desde esta fase ningun cambio de refactor UI se hace en `main` directamente;
  - no se modifica frontend todavia salvo que una subtarea posterior lo autorice.

### FRONT-2 - Extraer componentes compartidos minimos

- Objetivo: crear componentes Jinja compartidos de bajo riesgo para piezas repetidas.
- Alcance general:
  - flash messages;
  - paginacion;
  - headers simples;
  - badges o pills si aplica;
  - small wrappers reutilizables de layout si ayudan a reducir duplicacion.
- Riesgo: medio-bajo.
- Criterio de cierre:
  - hay componentes compartidos claramente reutilizables;
  - no cambia el comportamiento funcional visible;
  - se reduce duplicacion en templates sin tocar contratos de negocio.

### FRONT-3 - Normalizar estructura HTMX de Inbox/Vacancies

- Objetivo: alinear `list`, `detail` y `shell` de Vacancies sin cambiar el comportamiento visible.
- Alcance general:
  - revisar targets HTMX;
  - unificar estructura parcial del Inbox;
  - identificar y retirar dependencias residuales no necesarias;
  - preservar seleccion, filtros y paginacion.
- Riesgo: medio-alto.
- Criterio de cierre:
  - la estructura HTMX de Vacancies queda mas coherente;
  - Inbox mantiene equivalencia funcional;
  - no se rompen `selected`, `page`, `page_size`, `q` ni `view`.

### FRONT-4 - Mejorar Seguimiento de aplicaciones

- Objetivo: corregir jerarquia visual, estado seleccionado, filtros y detalle de Applications.
- Alcance general:
  - mejorar claridad list/detail;
  - corregir consistencia visual de fila seleccionada;
  - ordenar filtros y acciones frecuentes;
  - acercar patrones de Applications a los de Vacancies donde convenga.
- Riesgo: medio.
- Criterio de cierre:
  - Seguimiento tiene mejor legibilidad y consistencia;
  - las acciones HTMX siguen funcionando;
  - la pantalla queda mas uniforme respecto al resto del frontend.

### FRONT-5 - Reorganizar CSS por capas

- Objetivo: ordenar `app.css` por `tokens`, `base`, `layout`, `components` y `features`, sin rediseno total.
- Alcance general:
  - reordenar reglas;
  - documentar convenciones;
  - separar estilos globales de estilos de pantalla;
  - preparar el archivo para futuras extracciones seguras.
- Riesgo: medio-alto.
- Criterio de cierre:
  - el CSS queda mas navegable y mantenible;
  - no hay regresiones visuales relevantes;
  - se reduce el drift entre clases vivas y clases residuales.

### FRONT-6 - Dividir Profile en secciones recargables

- Objetivo: reducir el acoplamiento de `Profile` evitando el re-render completo de toda la pantalla.
- Alcance general:
  - separar secciones recargables;
  - reducir el alcance de swaps HTMX;
  - aislar mejor resumen, secciones de datos y vista CV;
  - preparar una futura simplificacion del armado de la pantalla.
- Riesgo: alto.
- Criterio de cierre:
  - `Profile` ya no depende de re-render global para cambios pequenos;
  - mejora la estabilidad de foco y scroll;
  - se conserva el comportamiento funcional esperado.

### FRONT-7 - Mejorar UX responsive y decision rapida

- Objetivo: ajustar experiencia movil o compacta y reforzar el frontend como herramienta de decision.
- Alcance general:
  - mejorar responsive de Inbox, Applications y Profile;
  - priorizar acciones como aplicar, descartar, siguiente accion y contexto de decision;
  - reforzar claridad visual sin una reescritura visual completa.
- Riesgo: medio.
- Criterio de cierre:
  - las pantallas clave funcionan mejor en anchos reducidos;
  - se refuerza el flujo de decision rapida;
  - se mantiene continuidad con la UI actual.

## 6. Flujo operativo por fase

Cada fase del refactor se trabajara despues como tareas y subtareas puntuales desde ChatGPT o Codex, usando siempre:

- prompt especifico para la tarea;
- rama ya creada y dedicada al refactor UI;
- alcance pequeno y verificable;
- validaciones acordes al riesgo;
- commit por tarea o por grupo coherente de cambios;
- reporte final con estado inicial, cambios, validaciones, riesgos y siguiente paso.

La intencion no es ejecutar fases grandes de una sola vez, sino mover el refactor como una secuencia de entregables pequenos, controlados y faciles de revertir si algo falla.

## 7. Validaciones base recomendadas

Comandos sugeridos para tareas con cambios de codigo:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_web_vacancies.py tests/test_web_applications.py tests/test_web_profile.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

Notas:

- no toda fase documental requiere correr toda la suite;
- toda fase con cambios de codigo si debe validar al menos lo proporcional a su alcance y riesgo;
- toda fase que toque Inbox, HTMX, partials o `Profile` debe tratar las validaciones como obligatorias, no opcionales.

## 8. Fuera de alcance inicial

- Migracion a React, Vue o Next.
- Reescritura total del frontend.
- Cambios en `chrome-extension/`.
- Cambios en modelo de datos.
- Cambios en analisis OpenAI.
- Cambios en SQL Server.
- Rediseno visual completo desde cero.

## 9. Primera accion despues de este documento

La siguiente tarea real sera `FRONT-1 - Preparar rama unica del refactor UI`.

Esa tarea debe:

- verificar `main` limpio;
- sincronizar `main` con `origin/main`;
- crear la rama `frontend/refactor-ui`;
- confirmar estado inicial read-only;
- no modificar frontend todavia salvo que una subtarea posterior lo defina.

Comandos iniciales sugeridos para esa futura tarea:

```powershell
git checkout main
git pull --ff-only origin main
git checkout -b frontend/refactor-ui
```

Regla operativa explicita:

- este documento queda en `main`;
- el refactor UI real empieza despues, en rama dedicada;
- a partir de `FRONT-1`, no deben hacerse cambios de refactor UI directamente sobre `main`.
