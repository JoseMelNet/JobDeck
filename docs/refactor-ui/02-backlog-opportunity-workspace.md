# FRONT-7 — Opportunity Workspace

## Conceptualización y backlog estratégico UI/UX

**Proyecto:** Job-Deck / CVs-Optimizator  
**Documento:** `docs/refactor-ui/02-backlog-opportunity-workspace.md`  
**Estado:** Propuesta estratégica para implementación incremental  
**Fecha:** 2026-05-24  
**Fase origen:** posterior al refactor estructural frontend  
**Documento anterior relacionado:** `docs/refactor-ui/01-backlog-estrategico-refactor-ui.md`

---

## 1. Contexto

El refactor estructural frontend ya fue cerrado e integrado a `main` mediante squash merge con el commit:

```text
Refactor frontend structure with Jinja and HTMX
```

Ese refactor dejó la base frontend suficientemente ordenada para abordar ahora un frente distinto: **mejora UI/UX orientada a operación real de búsqueda laboral**.

El objetivo de este nuevo frente no es solo mejorar la estética de la aplicación. El objetivo es convertirla en una herramienta de trabajo que permita:

- registrar vacantes con fricción mínima;
- revisar oportunidades rápidamente;
- decidir si una vacante merece atención;
- pasar vacantes a seguimiento;
- descartar vacantes sin ruido;
- gestionar aplicaciones activas;
- entender qué requiere acción;
- mantener el seguimiento laboral de forma clara.

La UI debe responder de forma rápida y visible:

- ¿Esta vacante vale la pena?
- ¿Qué tan buena es para mí?
- ¿Por qué aplicar o descartar?
- ¿Qué debo hacer ahora?
- ¿Qué ajuste de CV o acción sigue?
- ¿Qué aplicaciones requieren seguimiento?

---

## 2. Stack vigente

El frente se debe ejecutar manteniendo el stack actual:

- FastAPI;
- Jinja2;
- HTMX;
- SQL Server vía `pyodbc`;
- OpenAI para análisis de vacantes;
- extensión Chrome para captura desde LinkedIn;
- puerto local canónico: `8001`.

No se contempla migración inicial a React, Vue, Next ni otro frontend SPA.

---

## 3. Restricciones de diseño y ejecución

### 3.1 Restricciones técnicas

- No migrar de stack salvo razón técnica fuerte y documentada.
- No reescribir toda la aplicación.
- No mezclar rediseño visual con cambios profundos de persistencia.
- No tocar Profile funcionalmente en esta primera etapa.
- No diseñar mobile en esta fase; el objetivo inicial es desktop/navegador.
- No introducir drag-and-drop ni Kanban avanzado todavía.
- No crear campos inventados si no existen en datos reales.
- No cambiar prompts OpenAI salvo que una fase posterior lo justifique.

### 3.2 Restricciones de producto

- Reducir ruido visual.
- Eliminar botones repetidos o innecesarios.
- Priorizar acciones útiles.
- Evitar KPIs grandes si no ayudan a decidir.
- Mantener la aplicación simple y operativa.
- El usuario debe poder revisar, decidir y actuar sin recorrer una pantalla larga.

### 3.3 Restricciones de proceso

- Cada fase debe implementarse en PR pequeño o mediano.
- Cada fase debe tener validaciones automáticas.
- Cada fase con cambio visual debe tener smoke test manual.
- No avanzar a la siguiente fase si la anterior no está validada.
- Toda implementación debe partir de rama dedicada, inicialmente:

```text
frontend/decision-ux
```

---

## 4. Insumos de auditoría

Antes de definir este backlog se realizaron auditorías read-only sobre:

1. UI/UX general del frontend renderizado.
2. Contrato de datos de Vacancies / Vacancy Detail.
3. Applications / Seguimiento.
4. App Shell / header persistente.
5. Factibilidad del Opportunity Workspace.

Conclusiones consolidadas:

- El stack actual soporta el Opportunity Workspace sin migración.
- `base.html` ya ofrece un punto común para shell global.
- Vacancies es el entrypoint real de operación.
- El detalle inline de Vacancies debe eliminarse.
- Applications no debe pasar todavía a Kanban puro.
- Applications debe evolucionar primero a lista agrupada por estado + panel derecho.
- Profile queda fuera del primer frente, salvo compatibilidad mínima con layout global.
- El header global debe vivir en `base.html` y quedar fuera de swaps HTMX.
- La UI debe moverse hacia un patrón común de workspace con panel derecho.

---

## 5. Concepto principal: Opportunity Workspace

El nuevo frente se conceptualiza como un **Opportunity Workspace**.

Una vacante no debe tratarse como un registro aislado de una tabla. Debe tratarse como una oportunidad que fluye por estados de trabajo:

```text
capturada → evaluada → descartada / en seguimiento → aplicada → entrevista → oferta / cierre
```

El frontend debe reflejar ese flujo, pero sin implementar todavía un pipeline pesado.

La propuesta inicial es:

```text
Header global persistente
+ toolbar contextual por vista
+ workspace principal
  - panel izquierdo: lista, cola o agrupación
  - panel derecho: detalle, decisión y acciones
```

---

## 6. Arquitectura visual objetivo

### 6.1 Header global

Debe vivir en `base.html`.

Contenido recomendado:

- nombre/marca de la app;
- navegación principal:
  - Inbox;
  - Seguimiento;
  - Mi Perfil;
- CTA global:
  - Nueva Vacante.

No debe contener:

- KPIs grandes;
- filtros extensos;
- formularios;
- notas;
- acciones de detalle;
- bloques de ayuda largos.

En la primera fase no debe ser `sticky` ni `fixed`. Debe ser persistente como estructura global. Si más adelante se requiere comportamiento sticky, debe evaluarse solo para una franja superior compacta.

### 6.2 Toolbar contextual

Cada vista operativa puede tener una barra contextual compacta.

Para Vacancies:

- búsqueda;
- filtros;
- conteos compactos;
- estado de vista actual.

Para Applications:

- filtros por estado;
- conteos por grupo;
- búsqueda;
- vista actual.

La toolbar contextual debe reemplazar, no sumar, encabezados largos y KPIs redundantes.

### 6.3 Workspace principal

El workspace debe usar un patrón común:

```text
workspace-shell
  workspace-list / workspace-groups
  workspace-detail
```

No es obligatorio crear un componente Jinja único desde el primer PR, pero sí debe existir una convención visual y CSS compartida.

---

## 7. Conceptualización por vista

## 7.1 Inbox / Vacancies como cola de decisión

### Problema actual

La vista actual funciona como triage inicial, pero tiene varios problemas:

- el detalle inline hace crecer verticalmente la lista;
- la tarjeta detalle repite información de la fila madre;
- hay acciones repetidas;
- el usuario debe leer demasiado para decidir;
- la lista mezcla información de selección con información de análisis;
- no existe un panel de decisión claro.

### Dirección propuesta

Convertir Inbox en una **cola de decisión** con dos columnas:

```text
┌──────────────────────────┬──────────────────────────┐
│ Lista de vacantes        │ Panel de decisión         │
│                          │                          │
│ [score] Empresa          │ Empresa / Cargo           │
│ Cargo                    │ Score + decisión          │
│ decisión compacta        │ Resumen ejecutivo         │
│ fecha / estado           │ Por qué sí                │
│                          │ Riesgos                   │
│ [otra vacante]           │ Brechas / ajustes CV      │
│                          │ Acciones                  │
└──────────────────────────┴──────────────────────────┘
```

### Lista izquierda

Debe mostrar solo lo necesario para escoger una vacante:

- score;
- empresa;
- cargo;
- modalidad;
- fecha de registro;
- decisión o afinidad compacta;
- estado compacto.

No debe mostrar:

- botones repetidos;
- descripción completa;
- resumen largo;
- skills;
- gauge grande;
- link externo;
- detalle expandido.

### Panel derecho

Debe contener lo necesario para decidir:

- empresa y cargo como contexto;
- score;
- decisión de aplicación;
- resumen ejecutivo;
- fortalezas principales;
- riesgos principales;
- skills coincidentes;
- skills faltantes;
- ajustes CV recomendados;
- descripción completa si aporta;
- acciones principales.

Acciones recomendadas:

- primaria: pasar a seguimiento;
- primaria alternativa: descartar;
- secundaria: abrir link de la vacante.

### Datos que pueden usarse de inmediato

Para la primera versión no se requiere nuevo análisis OpenAI. Se pueden usar campos ya disponibles en el análisis:

- `score_total`;
- `decision_aplicacion`;
- `afinidad_general`;
- `fortalezas_principales`;
- `riesgos_principales`;
- `skills_match`;
- `skills_gap`;
- `encaje_estrategico`;
- `resumen_analisis`;
- `justificacion_decision`;
- `ajustes_cv_recomendados`;
- `seniority_inferido`;
- `salario_detectado`;
- `aspiracion_salarial_sugerida`.

### Datos que no deben inventarse

No deben introducirse como si fueran datos persistidos:

- prioridad;
- urgencia;
- fuente;
- fecha de publicación;
- ubicación;
- `message_hint`;
- `next_action` persistido.

Si se muestra una acción sugerida, debe ser derivada explícitamente desde datos existentes como `decision_aplicacion`, `has_application` y estado operativo.

---

## 7.2 Applications / Seguimiento como workspace operativo

### Problema actual

Applications ya intenta usar dos columnas, pero la experiencia no funciona bien:

- la lista sirve para localizar, no para operar seguimiento;
- el panel derecho mezcla resumen, quick actions, formulario largo y acción destructiva;
- hay acciones duplicadas;
- cambiar estado compite con editar, eliminar y leer notas;
- el análisis de la vacante desaparece al entrar a seguimiento;
- no responde bien qué aplicaciones requieren acción.

### Dirección propuesta

No implementar Kanban puro todavía.

La primera evolución debe ser:

```text
Lista agrupada por estado + panel derecho persistente
```

Ejemplo conceptual:

```text
┌─────────────────────────────┬──────────────────────────────┐
│ Pendiente                   │ Detalle operativo             │
│  - Empresa / Cargo          │ Empresa / Cargo               │
│  - Fecha / estado           │ Estado actual                 │
│                             │ Notas                         │
│ Aplicada                    │ Contacto                      │
│  - Empresa / Cargo          │ Link                          │
│                             │ Cambiar estado                │
│ Entrevista                  │ Acciones secundarias          │
└─────────────────────────────┴──────────────────────────────┘
```

### Lista / grupos

Debe mostrar:

- empresa;
- cargo;
- estado;
- fecha de aplicación o registro;
- modalidad si aporta;
- indicador compacto de notas/contacto si existe.

No debe mostrar:

- formularios;
- muchos botones;
- acciones destructivas;
- notas largas;
- contacto completo.

### Panel derecho

Debe contener:

- empresa y cargo;
- estado actual;
- transición de estado;
- link a la vacante;
- notas operativas;
- contacto/recruiter si existe;
- metadata de fechas;
- acción secundaria de rechazo/cierre;
- eliminación como acción terciaria y poco prominente.

### Estados actuales

Los estados actuales permiten agrupación, pero no justifican aún un pipeline visual completo. Estados identificados:

- `Pending`;
- `Applied`;
- `Technical Test`;
- `In Interview`;
- `Done`;
- `Rejected`;
- `Open Offer`.

Riesgo conocido:

- `Done` existe en enum y formulario, pero no está completamente integrado en filtros/quick actions.
- Los datos reales actuales se concentran principalmente en `Pending`, `Applied` y `Rejected`.
- Faltan `updated_at`, `next_action`, `target_date` y señales de urgencia.

Por eso, el destino inicial debe ser lista agrupada, no Kanban.

---

## 8. Decisiones cerradas para FRONT-7

1. **Mantener FastAPI + Jinja2 + HTMX.**
2. **No migrar a frontend SPA.**
3. **No implementar mobile en esta fase.**
4. **No rediseñar Profile funcionalmente en este frente.**
5. **No implementar Kanban/drag-and-drop como primera solución de Seguimiento.**
6. **No meter KPIs grandes en el header global.**
7. **No inventar campos de dominio no existentes.**
8. **No tocar OpenAI ni prompts para el primer rediseño.**
9. **Inbox debe abandonar detalle inline.**
10. **Applications debe evolucionar primero a lista agrupada por estado + panel derecho.**

---

## 9. Backlog estratégico propuesto

## FRONT-7.1 — Shell común y header persistente

### Objetivo

Preparar la estructura visual común del Opportunity Workspace, reduciendo duplicación de encabezados y creando una navegación global más limpia.

### Alcance

- Ajustar `base.html` como fuente del header global.
- Mantener el header fuera de swaps HTMX.
- Incluir navegación principal:
  - Inbox;
  - Seguimiento;
  - Mi Perfil.
- Incluir CTA global `Nueva Vacante`.
- Compactar headers internos redundantes en Inbox y Applications.
- Introducir o preparar una barra contextual por vista.
- Mantener Profile con cambios mínimos de compatibilidad.
- No hacer header sticky/fixed todavía.

### Fuera de alcance

- Rediseño funcional de Profile.
- Dashboard nuevo.
- Mobile.
- Kanban.
- Cambios de persistencia.

### Archivos probables

- `base.html`;
- componentes de header/page header;
- `vacancies/index.html`;
- `applications/index.html`;
- `vacancies/new.html` si requiere compactación visual;
- `app.css`.

### Riesgo

Bajo-medio.

Riesgos principales:

- duplicar header global + page headers internos;
- afectar spacing de Profile;
- dejar KPIs redundantes;
- tocar estilos globales demasiado amplios.

### Criterio de cierre

- Existe header global limpio.
- La navegación principal es consistente.
- `Nueva Vacante` está disponible como CTA global.
- Inbox y Applications no muestran doble encabezado pesado.
- Profile sigue funcionando sin rediseño funcional.

### Validaciones

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

Smoke test manual:

- abrir `/app/vacancies`;
- abrir `/app/applications`;
- abrir `/app/profile`;
- abrir `/app/vacancies/new`;
- verificar navegación principal;
- verificar que no haya duplicación visual grave de headers.

---

## FRONT-7.2 — Inbox master-detail

### Objetivo

Convertir Inbox en una cola de decisión con lista izquierda y panel derecho, eliminando el detalle inline.

### Alcance

- Reemplazar detalle inline por panel derecho.
- Separar conceptualmente lista y detalle.
- Preservar HTMX y `hx-push-url`.
- Mantener filtros y paginación.
- Compactar la lista de vacantes.
- Mover datos de análisis al panel derecho.
- Eliminar botones repetidos.
- Eliminar botón de cerrar detalle si deja de aplicar.
- Usar solo datos existentes.

### Lista izquierda debe mostrar

- score;
- empresa;
- cargo;
- modalidad;
- fecha;
- decisión/afinidad compacta;
- estado compacto.

### Panel derecho debe mostrar

- empresa/cargo;
- score;
- decisión;
- resumen ejecutivo;
- fortalezas;
- riesgos;
- skills match/gap;
- ajustes CV recomendados;
- descripción/link;
- acciones principales.

### Fuera de alcance

- Cambiar contrato OpenAI.
- Crear nuevos campos SQL.
- Implementar `message_hint`.
- Implementar prioridad/urgencia.
- Rediseñar Applications.
- Rediseñar Profile.

### Archivos probables

- `vacancies/index.html`;
- `vacancies/_shell.html`;
- `vacancies/_list.html`;
- `vacancies/_detail.html`;
- `vacancies/_filters.html`;
- `vacancies.py`;
- `app.css`;
- tests web de Vacancies.

### Riesgo

Medio.

Riesgos principales:

- pérdida de comportamiento de selección;
- cambios en targets HTMX;
- scroll/foco;
- paginación con selección activa;
- duplicación accidental de datos entre lista y panel.

### Criterio de cierre

- Seleccionar una vacante actualiza el panel derecho.
- La lista no crece verticalmente al seleccionar.
- El detalle inline anterior queda eliminado o inactivo.
- Los filtros siguen funcionando.
- La paginación sigue funcionando.
- `hx-push-url` se conserva.
- Las acciones `Seguimiento`, `Descartar` y `Abrir` están claras y no duplicadas.

### Validaciones

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

Smoke test manual:

- abrir `/app/vacancies`;
- seleccionar varias vacantes;
- filtrar por texto/estado/decisión si aplica;
- paginar;
- pasar una vacante a seguimiento;
- descartar una vacante;
- abrir link externo;
- verificar que no haya scroll brusco ni detalle inline duplicado.

---

## FRONT-7.3 — Applications agrupado por estado + panel derecho

### Objetivo

Convertir Seguimiento en un workspace operativo, agrupando aplicaciones por estado y limpiando el panel derecho.

### Alcance

- Reorganizar lista por grupos de estado.
- Mantener panel derecho persistente.
- Reducir acciones repetidas.
- Bajar prioridad visual de eliminar.
- Reorganizar edición de estado/notas/contacto.
- Mantener HTMX.
- No implementar Kanban drag-and-drop.
- No cambiar persistencia.

### Lista/grupos deben mostrar

- empresa;
- cargo;
- estado;
- fecha aplicación o registro;
- modalidad si aporta;
- señal compacta de notas/contacto si existe.

### Panel derecho debe mostrar

- empresa/cargo;
- estado actual;
- transición de estado;
- link;
- notas;
- contacto/recruiter;
- metadata de fechas;
- acciones secundarias.

### Fuera de alcance

- Drag-and-drop.
- Pipeline Kanban completo.
- `next_action` persistido.
- `target_date`.
- `updated_at`.
- rediseño de tabla SQL.
- múltiples aplicaciones por vacante.

### Archivos probables

- `applications/index.html`;
- `applications/_shell.html`;
- `applications/_list.html`;
- `applications/_detail.html`;
- `applications/_filters.html`;
- `applications.py`;
- `app.css`;
- tests web de Applications.

### Riesgo

Medio.

Riesgos principales:

- paginación por grupos;
- selección activa si cambia filtro;
- re-render de shell completo;
- estado `Done` inconsistente;
- panel derecho sobrecargado.

### Criterio de cierre

- Las aplicaciones se entienden por estado.
- La vista responde mejor “qué está pendiente”.
- El panel derecho deja de ser un formulario largo dominante.
- Cambiar estado sigue funcionando.
- Editar notas/contacto sigue funcionando.
- Eliminar existe, pero con menor prominencia visual.

### Validaciones

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

Smoke test manual:

- abrir `/app/applications`;
- cambiar filtros por estado;
- seleccionar aplicaciones en distintos estados;
- cambiar estado;
- editar notas;
- verificar contacto/recruiter;
- verificar que el panel derecho conserve contexto;
- verificar que no haya acciones repetidas con la misma prioridad visual.

---

## FRONT-7.4 — Limpieza visual común del Opportunity Workspace

### Objetivo

Normalizar el lenguaje visual de Inbox y Applications después de validar los dos layouts principales.

### Alcance

- Normalizar botones primarios/secundarios/terciarios.
- Normalizar badges y pills.
- Normalizar cards de oportunidad.
- Normalizar paneles derechos.
- Normalizar toolbars contextuales.
- Revisar estados vacíos.
- Revisar flashes y mensajes de feedback.
- Reducir CSS obsoleto asociado a detalle inline.

### Fuera de alcance

- Fragmentar `app.css` en múltiples archivos.
- Rediseñar Profile.
- Dashboard nuevo.
- Mobile.

### Archivos probables

- `app.css`;
- componentes compartidos;
- templates de Vacancies;
- templates de Applications;
- tests visuales/manuales.

### Riesgo

Medio.

Riesgos principales:

- tocar clases globales que afectan Profile;
- mezclar estilos de feature con estilos globales;
- introducir inconsistencias por limpiar demasiado rápido.

### Criterio de cierre

- Inbox y Applications se sienten parte del mismo producto.
- Las acciones primarias son visualmente claras.
- Las acciones secundarias no compiten con las primarias.
- Las acciones destructivas tienen baja prominencia.
- No hay duplicación evidente de headers, botones o paneles.

### Validaciones

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

Smoke test manual:

- Inbox completo;
- Applications completo;
- Profile carga sin regresión visual grave;
- Nueva Vacante carga sin regresión visual grave.

---

## FRONT-7.5 — Contrato operativo mínimo de Seguimiento

### Objetivo

Preparar una evolución futura de Applications hacia seguimiento operativo real, agregando o exponiendo señales que hoy no existen o no llegan a UI.

### Motivación

El rediseño visual puede mejorar mucho la vista actual, pero el seguimiento real requiere datos adicionales que hoy no están presentes o no están bien expuestos.

Faltantes identificados:

- última actividad;
- próxima acción;
- fecha objetivo;
- motivo de rechazo/cierre;
- análisis heredado resumido;
- señal de seguimiento vencido;
- normalización de `Done`;
- posible exposición de fecha de captura de vacante.

### Alcance tentativo

- Diagnóstico técnico previo.
- Definir contrato mínimo.
- Decidir si requiere migración SQL.
- Exponer análisis heredado mínimo en Applications si aplica.
- Resolver inconsistencia de `Done`.

### Fuera de alcance

- Kanban drag-and-drop.
- Automatizaciones complejas.
- Reintentos múltiples por vacante.
- Rediseño completo de persistencia.

### Riesgo

Medio-alto.

### Criterio de cierre

- Existe una propuesta técnica clara para enriquecer Seguimiento.
- Se sabe qué campos son derivados y cuáles persistidos.
- No se introducen datos ambiguos o inventados.

---

## 10. Orden recomendado de implementación

Orden recomendado:

```text
FRONT-7.1 — Shell común y header persistente
FRONT-7.2 — Inbox master-detail
FRONT-7.3 — Applications agrupado por estado + panel derecho
FRONT-7.4 — Limpieza visual común
FRONT-7.5 — Contrato operativo mínimo de Seguimiento
```

Si se busca acelerar el primer impacto visible, FRONT-7.1 y FRONT-7.2 pueden ejecutarse en una misma fase controlada, siempre que no se incluya Applications en ese mismo PR.

---

## 11. Primer PR recomendado

El primer PR seguro debería cubrir:

```text
Shell común + preparación de workspace visual + Inbox sin detalle inline
```

Alcance máximo del primer PR:

- header global limpio;
- compactación de headers redundantes en Inbox;
- patrón inicial de workspace;
- Inbox en dos columnas;
- panel derecho de decisión;
- eliminación de detalle inline;
- preservación de HTMX y `hx-push-url`.

No debe incluir:

- rediseño de Applications;
- Kanban;
- Profile;
- cambios SQL;
- cambios OpenAI;
- dashboard nuevo;
- mobile.

---

## 12. Validaciones estándar por fase

Comandos obligatorios desde el entorno virtual del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall app tests
```

No usar `pytest` si no está instalado en el venv.

---

## 13. Smoke tests manuales mínimos

### Para Inbox

- abrir `/app/vacancies`;
- seleccionar vacantes;
- filtrar;
- paginar;
- pasar a seguimiento;
- descartar;
- abrir link;
- verificar que la lista no crezca verticalmente;
- verificar que no haya acciones duplicadas.

### Para Applications

- abrir `/app/applications`;
- seleccionar aplicación;
- filtrar por estado;
- cambiar estado;
- editar notas;
- revisar contacto;
- verificar que eliminar no compita con acciones primarias.

### Para shell global

- navegar entre Inbox, Seguimiento, Mi Perfil y Nueva Vacante;
- confirmar que header no se duplica;
- confirmar que Profile carga sin regresión funcional;
- confirmar que no hay errores visibles en consola.

---

## 14. Riesgos transversales

- Intentar rediseñar demasiadas vistas en un solo PR.
- Convertir Applications en Kanban antes de tener datos operativos suficientes.
- Afectar Profile al tocar clases globales.
- Duplicar header global, page headers y barras contextuales.
- Mantener acciones repetidas en lista y panel.
- Reintroducir formularios largos como superficie dominante.
- Depender de campos inexistentes como prioridad, urgencia o `message_hint`.
- Tocar OpenAI o persistencia antes de validar el nuevo workspace visual.

---

## 15. Criterio de éxito del frente FRONT-7

El frente se considera exitoso cuando:

- Inbox permite decidir rápidamente si una vacante se descarta o pasa a seguimiento.
- La lista de vacantes no crece verticalmente con detalles inline.
- El panel derecho concentra análisis, contexto y acciones.
- Seguimiento permite entender aplicaciones por estado.
- El panel derecho de Applications permite operar sin competir con formularios largos.
- La aplicación tiene header global claro.
- La UI contiene menos ruido y menos duplicación.
- Se mantiene FastAPI + Jinja2 + HTMX.
- Profile no sufre regresiones por cambios globales.

---

## 16. Estado final de este documento

Este documento reemplaza la idea inicial de un rediseño UI/UX amplio por un frente más específico:

```text
Opportunity Workspace para Inbox y Seguimiento
```

Profile, Dashboard, mobile, Kanban avanzado y enriquecimiento profundo de contrato quedan para fases posteriores.
