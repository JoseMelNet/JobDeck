-- ============================================================
-- 08_cvs_base.sql
-- CVs base del usuario, uno por tipo de rol.
-- Cada CV es una selección estratégica y narrativa
-- del perfil, orientada a un tipo de cargo específico.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE cvs_base (
    id                      INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id               INT                 NOT NULL
        CONSTRAINT FK_cvs_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Identificación del CV
    nombre_rol              NVARCHAR(150)       NOT NULL,
    -- Ej: "Data Analyst", "BI Developer", "Data Engineer"

    -- Resumen profesional narrativo
    -- Texto de 3-5 líneas orientado al rol
    resumen_profesional     NVARCHAR(MAX)       NOT NULL,

    -- IDs de experiencias seleccionadas para este CV
    -- JSON array de IDs: [1, 3, 5]
    -- Referencia a perfil_experiencia_laboral.id
    experiencias_ids        NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- IDs de proyectos seleccionados para este CV
    -- JSON array de IDs: [2, 4]
    -- Referencia a perfil_proyectos.id
    proyectos_ids           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- IDs de skills seleccionadas y su orden de aparición
    -- JSON array de IDs: [1, 4, 7, 2]
    -- Referencia a perfil_skills.id
    skills_ids              NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- IDs de cursos y certificaciones a incluir
    cursos_ids              NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
    certificaciones_ids     NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- IDs de educación a incluir
    educacion_ids           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',

    -- Control
    activo                  BIT                 NOT NULL DEFAULT 1,
    fecha_creacion          DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion     DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_cvs_base_perfil_id
    ON cvs_base(perfil_id);
GO

PRINT '✓ Tabla cvs_base creada correctamente.';
GO
