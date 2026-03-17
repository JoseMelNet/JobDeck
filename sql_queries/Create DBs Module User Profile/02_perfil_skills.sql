-- ============================================================
-- 02_perfil_skills.sql
-- Skills técnicas, blandas e idiomas del usuario.
-- Los idiomas se manejan como categoría "Idiomas" dentro
-- de esta misma tabla para simplificar el modelo.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_skills (
    id              INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id       INT                 NOT NULL
        CONSTRAINT FK_skills_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Categorías sugeridas:
    -- "Bases de Datos", "Visualización", "Lenguajes de Programación",
    -- "Cloud", "ETL / Integración", "Herramientas", "Blandas", "Idiomas"
    categoria       NVARCHAR(100)       NOT NULL,
    skill           NVARCHAR(100)       NOT NULL,

    -- Nivel técnico:   Básico / Intermedio / Avanzado / Experto
    -- Nivel idioma:    A1 / A2 / B1 / B2 / C1 / C2 / Nativo
    nivel           NVARCHAR(20)        NOT NULL,

    -- Control
    fecha_creacion  DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_perfil_skills_perfil_id
    ON perfil_skills(perfil_id);
GO

CREATE INDEX IX_perfil_skills_categoria
    ON perfil_skills(perfil_id, categoria);
GO

PRINT '✓ Tabla perfil_skills creada correctamente.';
GO
