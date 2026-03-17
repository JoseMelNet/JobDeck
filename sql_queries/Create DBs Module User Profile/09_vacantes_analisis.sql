-- ============================================================
-- 09_vacantes_analisis.sql
-- Resultado del análisis de afinidad entre una vacante,
-- el perfil del usuario y un CV base seleccionado.
-- Relación 1:1 con vacantes. Re-analizable sin perder datos.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE vacantes_analisis (
    id                          INT IDENTITY(1,1)   PRIMARY KEY,

    -- Relaciones
    vacante_id                  INT                 NOT NULL
        CONSTRAINT FK_analisis_vacante REFERENCES vacantes(id)
            ON DELETE CASCADE,
    perfil_id                   INT                 NOT NULL
        CONSTRAINT FK_analisis_perfil REFERENCES perfil_usuario(id),
    cv_base_id                  INT                 NULL
        CONSTRAINT FK_analisis_cv REFERENCES cvs_base(id),
    -- NULL si se analizó sin seleccionar un CV base

    -- ── INSIGHTS EXTRAÍDOS DE LA VACANTE (por OpenAI) ────────

    -- Skills que la vacante requiere
    -- JSON: [{"skill":"SQL","tipo":"requerido"},{"skill":"Tableau","tipo":"deseable"}]
    skills_requeridas           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- Skills blandas mencionadas en la vacante
    -- JSON: ["comunicación", "trabajo en equipo"]
    skills_blandas_detectadas   NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- Seniority inferido con justificación
    seniority_inferido          NVARCHAR(20)        NOT NULL DEFAULT 'No especificado'
        CONSTRAINT CK_seniority CHECK (seniority_inferido IN (
            'Junior', 'Mid', 'Senior', 'No especificado'
        )),
    justificacion_seniority     NVARCHAR(MAX)       NULL,
    -- Texto explicando por qué se infirió ese nivel

    -- Modalidad detectada en el texto de la vacante
    modalidad_detectada         NVARCHAR(20)        NULL,

    -- Salario mencionado (string porque viene en formatos variables)
    -- Ej: "3.000.000 - 5.000.000 COP", "$2,000 USD", "No especificado"
    salario_detectado           NVARCHAR(150)       NULL,

    -- Idiomas requeridos
    -- JSON: [{"idioma":"Inglés","nivel":"B2"}]
    idiomas_requeridos          NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- ── SCORING (0 a 100) ────────────────────────────────────

    score_total                 DECIMAL(5,2)        NOT NULL DEFAULT 0,
    score_skills_tecnicas       DECIMAL(5,2)        NOT NULL DEFAULT 0,
    score_seniority             DECIMAL(5,2)        NOT NULL DEFAULT 0,
    score_modalidad             DECIMAL(5,2)        NOT NULL DEFAULT 0,
    score_idiomas               DECIMAL(5,2)        NOT NULL DEFAULT 0,
    score_skills_blandas        DECIMAL(5,2)        NOT NULL DEFAULT 0,

    -- Verde >= 70 | Amarillo 40-69 | Rojo < 40 | Gris = sin analizar
    semaforo                    NVARCHAR(10)        NOT NULL DEFAULT 'gris'
        CONSTRAINT CK_semaforo CHECK (semaforo IN (
            'verde', 'amarillo', 'rojo', 'gris'
        )),

    -- ── REPORTE NARRATIVO (generado por OpenAI) ─────────────

    resumen_analisis            NVARCHAR(MAX)       NULL,
    -- Párrafo con el análisis general de la vacante

    -- Skills que el usuario SÍ tiene de las requeridas
    -- JSON: ["SQL", "Power BI", "Python"]
    skills_match                NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- Skills que la vacante pide y el usuario NO tiene
    -- JSON: ["Tableau", "dbt", "Spark"]
    skills_gap                  NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- Aspiración salarial recomendada según el análisis
    aspiracion_salarial_sugerida NVARCHAR(150)      NULL,
    -- Ej: "4.500.000 - 6.000.000 COP"

    -- ── SUGERENCIAS PARA EL CV ───────────────────────────────

    sugerencias_cv              NVARCHAR(MAX)       NULL,
    -- Texto narrativo con recomendaciones específicas para
    -- adaptar el CV base a esta vacante

    -- ── CONTROL ──────────────────────────────────────────────

    fecha_analisis              DATETIME            NOT NULL DEFAULT GETDATE()
    -- Permite saber si el análisis está desactualizado
    -- respecto a cambios en el perfil
);
GO

CREATE UNIQUE INDEX IX_vacantes_analisis_vacante_id
    ON vacantes_analisis(vacante_id);
-- UNIQUE porque la relación es 1:1 con vacantes.
-- Para re-analizar se hace UPDATE, no INSERT.
GO

CREATE INDEX IX_vacantes_analisis_semaforo
    ON vacantes_analisis(semaforo);
-- Útil para filtrar vacantes por semáforo en Mis Vacantes.
GO

PRINT '✓ Tabla vacantes_analisis creada correctamente.';
GO
