-- ============================================================
-- 07_perfil_certificaciones.sql
-- Certificaciones profesionales del usuario.
-- A diferencia de cursos, las certificaciones tienen
-- vigencia y son emitidas por entidades reconocidas.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_certificaciones (
    id                  INT IDENTITY(1,1)   PRIMARY KEY,
    perfil_id           INT                 NOT NULL
        CONSTRAINT FK_certificaciones_perfil REFERENCES perfil_usuario(id)
            ON DELETE CASCADE,

    -- Datos de la certificación
    titulo              NVARCHAR(200)       NOT NULL,
    -- Ej: "AWS Certified Data Analytics", "PL-300 Power BI"

    institucion         NVARCHAR(150)       NOT NULL,
    -- Ej: "Amazon Web Services", "Microsoft", "Google"

    -- Fechas
    fecha_obtencion     DATE                NOT NULL,
    fecha_vencimiento   DATE                NULL,
    -- NULL si la certificación no vence

    status              NVARCHAR(20)        NOT NULL DEFAULT 'Vigente'
        CONSTRAINT CK_cert_status CHECK (status IN (
            'Vigente',
            'Vencido',
            'En proceso'
        )),

    url_certificado     NVARCHAR(300)       NULL,
    -- Link a Credly, LinkedIn, o página del emisor

    -- Control
    fecha_creacion      DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_certificaciones_perfil_id
    ON perfil_certificaciones(perfil_id);
GO

PRINT '✓ Tabla perfil_certificaciones creada correctamente.';
GO
