-- ============================================================
-- 05_perfil_educacion.sql
-- Formación académica del usuario.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_educacion (
    id              INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id       INT                 NOT NULL
        CONSTRAINT FK_educacion_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Datos académicos
    titulo          NVARCHAR(200)       NOT NULL,
    -- Ej: "Ingeniería de Sistemas", "Administración de Empresas"

    institucion     NVARCHAR(200)       NOT NULL,
    ciudad          NVARCHAR(100)       NULL,

    nivel           NVARCHAR(50)        NOT NULL
        CONSTRAINT CK_educacion_nivel CHECK (nivel IN (
            'Bachillerato',
            'Técnico',
            'Tecnólogo',
            'Pregrado',
            'Especialización',
            'Maestría',
            'Doctorado',
            'Otro'
        )),

    -- Fechas
    fecha_inicio    DATE                NOT NULL,
    fecha_fin       DATE                NULL,

    status          NVARCHAR(20)        NOT NULL DEFAULT 'Completado'
        CONSTRAINT CK_educacion_status CHECK (status IN (
            'En curso',
            'Completado',
            'Pausado',
            'Abandonado'
        )),

    -- Control
    fecha_creacion  DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_educacion_perfil_id
    ON perfil_educacion(perfil_id);
GO

PRINT '✓ Tabla perfil_educacion creada correctamente.';
GO
