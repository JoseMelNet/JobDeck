-- ============================================================
-- 06_perfil_cursos.sql
-- Cursos tomados por el usuario (Udemy, Coursera, etc.)
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_cursos (
    id              INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id       INT                 NOT NULL
        CONSTRAINT FK_cursos_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Datos del curso
    titulo          NVARCHAR(200)       NOT NULL,
    institucion     NVARCHAR(150)       NOT NULL,
    -- Ej: "Udemy", "Coursera", "Platzi", "LinkedIn Learning"

    -- Fechas
    fecha_inicio    DATE                NULL,
    fecha_fin       DATE                NULL,

    status          NVARCHAR(20)        NOT NULL DEFAULT 'Completado'
        CONSTRAINT CK_cursos_status CHECK (status IN (
            'En curso',
            'Completado',
            'Pausado'
        )),

    url_certificado NVARCHAR(300)       NULL,
    -- Link al certificado en línea (Udemy, Coursera, etc.)

    -- Control
    fecha_creacion  DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_cursos_perfil_id
    ON perfil_cursos(perfil_id);
GO

PRINT '✓ Tabla perfil_cursos creada correctamente.';
GO
