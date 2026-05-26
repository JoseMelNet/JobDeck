# PROFILE-1 - Perfil Laboral

## Diagnostico actual

El modulo actual de `Mi Perfil` ya cubre el flujo principal del producto, pero mezcla en una sola pagina:

- datos estrategicos para decidir si aplicar;
- datos de contacto y salida;
- signals para analisis;
- evidencia profesional;
- credenciales;
- vista CV.

Hallazgos principales:

- `app/interfaces/web/routes/profile.py` concentra rutas, armado de contexto y parte de la composicion de la vista CV.
- el bloque `Datos principales` mezcla objetivo laboral, preferencias, contacto y salidas;
- `Skills` si alimenta analisis y vista CV, pero su contrato HTMX depende de refresh parciales fragiles;
- `Proyectos` existe como bloque relevante, pero hoy no entra ni al payload de analisis ni a la vista CV;
- `Estado del perfil` todavia comunica preocupaciones internas del sistema en lugar de proxima accion de producto.

## Arquitectura funcional propuesta

La evolucion recomendada del modulo es:

1. `Resumen`
   - calidad del perfil;
   - cobertura por uso;
   - siguiente accion recomendada.
2. `Objetivo`
   - rol objetivo;
   - seniority;
   - modalidad;
   - ubicacion;
   - compensacion;
   - restricciones para decidir si aplicar.
3. `Senales`
   - skills;
   - herramientas;
   - lenguajes;
   - idiomas;
   - prioridad de matching.
4. `Evidencia`
   - experiencias;
   - proyectos;
   - logros;
   - impacto;
   - stack asociado.
5. `Credenciales`
   - educacion;
   - cursos;
   - certificaciones.
6. `Salidas`
   - CV base;
   - contacto;
   - resumen profesional;
   - futuros CVs adaptados y mensajes.

## Mapa de bloques actuales hacia la arquitectura nueva

| Bloque actual | Seccion futura principal | Uso esperado | Observacion |
| --- | --- | --- | --- |
| `overview` | `Resumen` | cobertura y proxima accion | debe dejar de ser solo contador |
| `Datos principales` | `Objetivo` + `Salidas` | matching, estrategia y contacto | hoy mezcla demasiadas responsabilidades |
| `Skills` | `Senales` | analisis, CV, brechas, estrategia | es el bloque mas directamente conectado al matching |
| `Experiencia` | `Evidencia` | analisis, CV, mensajes, entrevistas | ya aporta a analisis y CV |
| `Proyectos` | `Evidencia` | CV adaptado, mensajes, entrevistas | hoy queda aislado del resto |
| `Educacion` | `Credenciales` | soporte de matching y CV | no debe competir visualmente con evidencia |
| `Cursos` | `Credenciales` | soporte de matching y CV | mejor como refuerzo, no como centro |
| `Certificaciones` | `Credenciales` | soporte de matching y CV | igual que cursos |
| `Estado del perfil` | `Resumen` | calidad y accion sugerida | debe reemplazar mensajes internos como migracion |
| `Vista CV` | `Salidas` | salida consolidada | debe desacoplarse del route con el tiempo |

## Mapa de campos actuales

El mapa canonico campo por campo vive en:

- `app/interfaces/web/presentation/profile_view_model.py`

Resumen por grupos:

- `perfil_usuario.nombre`
  - seccion: `Salidas`
  - usos: salida, mensajes
  - nota: hoy tambien viaja al payload de analisis, pero no es signal de matching
- `perfil_usuario.titulo_profesional`, `nivel_actual`, `anos_experiencia`, `salario_min`, `salario_max`, `moneda`, `modalidades_aceptadas`, `ciudad`
  - seccion: `Objetivo`
  - usos: analisis, estrategia, salida
- `perfil_usuario.correo`, `celular`, `perfil_linkedin`, `perfil_github`, `direccion`
  - seccion: `Salidas`
  - usos: contacto y mensajes
  - nota: `direccion` es secundaria y candidata a ocultarse
- `perfil_skills.categoria`, `skill`, `nivel`
  - seccion: `Senales`
  - usos: analisis, CV, estrategia, mensajes
- `perfil_experiencia_laboral.*`
  - seccion: `Evidencia`
  - usos: analisis, CV, mensajes, estrategia
  - nota: `descripcion_empresa` es soporte, no signal principal
- `perfil_proyectos.*`
  - seccion: `Evidencia`
  - usos: CV futuro, mensajes, estrategia
  - nota: hoy no participa en analisis ni vista CV
- `perfil_educacion.*`
  - seccion: `Credenciales`
  - usos: analisis, CV, estrategia
- `perfil_cursos.*`
  - seccion: `Credenciales`
  - usos: soporte de analisis y CV
  - nota: fechas y URL son soporte secundario
- `perfil_certificaciones.*`
  - seccion: `Credenciales`
  - usos: soporte de analisis y CV
  - nota: `fecha_vencimiento` y `url_certificado` son soporte secundario

## Clasificacion por uso

- `Analisis de vacantes`
  - objetivo laboral;
  - skills;
  - experiencias;
  - credenciales clave.
- `CV base`
  - identidad profesional;
  - contacto;
  - skills;
  - experiencias;
  - credenciales;
  - proyectos como evidencia futura.
- `Cartas y mensajes`
  - nombre;
  - contacto;
  - objetivo;
  - evidencias;
  - links de salida.
- `Estrategia`
  - objetivo laboral;
  - modalidades;
  - compensacion;
  - senales;
  - evidencia reusable;
  - industrias y restricciones cuando existan.
- `Solo salida/contacto`
  - correo;
  - celular;
  - LinkedIn;
  - GitHub;
  - direccion.
- `Secundario o candidato a ocultarse`
  - direccion;
  - descripcion_empresa;
  - URLs de certificados;
  - fechas de soporte que no cambian el matching.

## Navegacion interna propuesta

Orden recomendado para la futura navegacion:

1. `Resumen`
2. `Objetivo`
3. `Senales`
4. `Evidencia`
5. `Credenciales`
6. `Salidas`

La navegacion debe ser interna al modulo, no en el layout global. Puede arrancar como tabs livianos o filtros locales sin redisenar todavia toda la pagina.

## Contrato de presentacion propuesto

El contrato minimo queda expresado en `profile_view_model.py` y define:

- secciones funcionales estables;
- bloques actuales y su destino funcional;
- campos actuales y su seccion futura;
- usos objetivo por campo;
- consumidores actuales reales;
- prioridad `core`, `supporting` o `secondary`.

ViewModel sugerido para la siguiente fase:

```python
{
    "sections": [...],
    "blocks": [...],
    "fields": [...],
    "summary": {
        "analysis_coverage": ...,
        "cv_coverage": ...,
        "evidence_coverage": ...,
        "next_action": ...,
    },
}
```

La siguiente fase puede construir datos concretos sobre este contrato sin reescribir todavia el CRUD ni la persistencia.

## Riesgos

- mover UI sin este contrato mantendria la mezcla actual de responsabilidades;
- integrar proyectos al analisis antes de ordenar evidencia generaria deuda adicional;
- tocar `profile.py` demasiado pronto mezclaria otra vez presentacion y flujo;
- ocultar campos sin clasificacion previa puede romper futuros casos de salida o mensajes.

## Backlog posterior sugerido

1. `PROFILE-2` - introducir `Resumen` real con cobertura y proxima accion.
2. `PROFILE-3` - separar `Objetivo` de `Salidas` en la UI sin cambiar CRUD.
3. `PROFILE-4` - estabilizar contratos HTMX por seccion usando el contrato funcional.
4. `PROFILE-5` - desacoplar la composicion de la vista CV fuera de `profile.py`.
5. `PROFILE-6` - reorganizar `Evidencia` para acercar proyectos a experiencias sin cambiar schema.
