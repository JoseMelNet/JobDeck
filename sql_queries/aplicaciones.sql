-- ============================================================
-- aplicaciones.sql
-- Script para crear la tabla "aplicaciones" en SQL Server
-- Ejecutar en SSMS sobre la BD job_postings_mvp
-- ============================================================

USE job_postings_mvp;
GO

-- Crear tabla aplicaciones
CREATE TABLE aplicaciones (
    id                  INT IDENTITY(1,1)   PRIMARY KEY,
    vacante_id          INT                 NOT NULL,
    fecha_aplicacion    DATETIME            NOT NULL,
    estado              VARCHAR(20)         NOT NULL DEFAULT 'Pendiente',
    nombre_recruiter    VARCHAR(150)        NULL,
    email_recruiter     VARCHAR(200)        NULL,
    telefono_recruiter  VARCHAR(50)         NULL,
    notas               NVARCHAR(MAX)       NULL,
    fecha_registro      DATETIME            NOT NULL DEFAULT GETDATE(),

    -- FK hacia tabla vacantes
    CONSTRAINT fk_aplicaciones_vacante
        FOREIGN KEY (vacante_id)
        REFERENCES vacantes(id)
        ON DELETE CASCADE,

    -- Evitar duplicados: 1 aplicación por vacante
    CONSTRAINT uq_aplicacion_vacante
        UNIQUE (vacante_id),

    -- Estados válidos
    CONSTRAINT chk_estado_aplicacion
        CHECK (estado IN ('Pendiente', 'Entrevista', 'Rechazado', 'Oferta'))
);
GO

-- Índice para búsquedas por estado
CREATE INDEX idx_aplicaciones_estado
    ON aplicaciones (estado);
GO

-- Índice para búsquedas por fecha
CREATE INDEX idx_aplicaciones_fecha
    ON aplicaciones (fecha_aplicacion DESC);
GO

-- Verificar creación
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'aplicaciones'
ORDER BY ORDINAL_POSITION;
GO

PRINT '✅ Tabla aplicaciones creada exitosamente';
GO
