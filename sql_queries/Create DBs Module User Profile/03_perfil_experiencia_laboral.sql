-- ============================================================
-- 03_perfil_experiencia_laboral.sql
-- Historial de experiencia laboral del usuario.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_experiencia_laboral (
    id                  INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id           INT                 NOT NULL
        CONSTRAINT FK_experiencia_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Datos del cargo
    cargo               NVARCHAR(150)       NOT NULL,
    empresa             NVARCHAR(150)       NOT NULL,
    ciudad              NVARCHAR(100)       NULL,

    -- Fechas
    fecha_inicio        DATE                NOT NULL,
    fecha_fin           DATE                NULL,
    es_trabajo_actual   BIT                 NOT NULL DEFAULT 0,
    -- Si es_trabajo_actual = 1, fecha_fin puede ser NULL

    -- Descripción
    descripcion_empresa NVARCHAR(300)       NULL,
    -- Breve contexto de la empresa (sector, tamaño, etc.)

    funciones           NVARCHAR(MAX)       NULL,
    -- Texto libre. Ej: "Diseño de dashboards en Power BI, gestión de ETL..."

    logros              NVARCHAR(MAX)       NULL,
    -- Texto libre con métricas. Ej: "Reduje tiempo de reporte en 40%..."

    -- Control
    fecha_creacion      DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_experiencia_perfil_id
    ON perfil_experiencia_laboral(perfil_id);
GO

PRINT '✓ Tabla perfil_experiencia_laboral creada correctamente.';
GO
