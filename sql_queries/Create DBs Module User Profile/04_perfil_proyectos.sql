-- ============================================================
-- 04_perfil_proyectos.sql
-- Proyectos relevantes del usuario (personales o laborales).
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_proyectos (
    id                  INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id           INT                 NOT NULL
        CONSTRAINT FK_proyectos_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Datos del proyecto
    nombre              NVARCHAR(150)       NOT NULL,
    empresa             NVARCHAR(150)       NULL,
    -- NULL si es proyecto personal
    ciudad              NVARCHAR(100)       NULL,

    -- Fechas
    fecha_inicio        DATE                NOT NULL,
    fecha_fin           DATE                NULL,
    es_proyecto_actual  BIT                 NOT NULL DEFAULT 0,

    -- Stack tecnológico (texto libre separado por comas)
    -- Ej: "Python, SQL, Power BI, Azure Data Factory"
    stack               NVARCHAR(500)       NULL,

    -- Descripción
    funciones           NVARCHAR(MAX)       NULL,
    -- Qué hiciste en el proyecto

    logros              NVARCHAR(MAX)       NULL,
    -- Resultados / impacto medible

    url_repositorio     NVARCHAR(300)       NULL,
    -- Link a GitHub, GitLab, etc.

    -- Control
    fecha_creacion      DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_proyectos_perfil_id
    ON perfil_proyectos(perfil_id);
GO

PRINT '✓ Tabla perfil_proyectos creada correctamente.';
GO
