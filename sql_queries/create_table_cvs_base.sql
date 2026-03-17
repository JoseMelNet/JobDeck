-- ============================================================
-- TABLA: cvs_base
-- Un CV por tipo de rol. Referencia al perfil del usuario.
-- ============================================================

CREATE TABLE cvs_base (
    id                      INT IDENTITY(1,1) PRIMARY KEY,

    -- Relación con el perfil
    perfil_id               INT             NOT NULL
        REFERENCES perfil_usuario(id),

    -- Identificación del CV
    nombre_rol              NVARCHAR(150)   NOT NULL,
    -- Ej: "Data Analyst", "BI Developer", "Data Engineer"

    -- Secciones narrativas del CV (texto libre editable)
    resumen_profesional     NVARCHAR(MAX)   NOT NULL,

    -- Secciones estructuradas (JSON) — misma estructura que perfil
    -- pero con orden y peso estratégico decidido por el usuario
    experiencia_destacada   NVARCHAR(MAX)   NOT NULL DEFAULT '[]',
    skills_destacadas       NVARCHAR(MAX)   NOT NULL DEFAULT '[]',
    cursos_certificaciones  NVARCHAR(MAX)   NOT NULL DEFAULT '[]',
    proyectos               NVARCHAR(MAX)   NOT NULL DEFAULT '[]',
    -- Ej proyectos: [{"nombre":"Dashboard ventas","descripcion":"...","tecnologias":["Power BI","SQL"]}]

    -- Control
    activo                  BIT             NOT NULL DEFAULT 1,
    fecha_creacion          DATETIME        NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion     DATETIME        NOT NULL DEFAULT GETDATE()
);

GO

CREATE INDEX IX_cvs_base_perfil_id
    ON cvs_base(perfil_id);

GO