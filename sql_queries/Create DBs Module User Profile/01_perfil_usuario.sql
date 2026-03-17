-- ============================================================
-- 01_perfil_usuario.sql
-- Tabla central del perfil profesional del usuario.
-- Preparada para escalar a multi-usuario agregando user_id.
-- ============================================================

USE job_postings_mvp;
GO

CREATE TABLE perfil_usuario (
    id                      INT IDENTITY(1,1)   PRIMARY KEY,

    -- Información personal
    nombre                  NVARCHAR(100)       NOT NULL,
    titulo_profesional      NVARCHAR(150)       NOT NULL,
    ciudad                  NVARCHAR(100)       NULL,
    direccion               NVARCHAR(200)       NULL,
    celular                 NVARCHAR(30)        NULL,
    correo                  NVARCHAR(150)       NULL,
    perfil_linkedin         NVARCHAR(300)       NULL,
    perfil_github           NVARCHAR(300)       NULL,

    -- Nivel y aspiración
    nivel_actual            NVARCHAR(20)        NOT NULL
        CONSTRAINT CK_perfil_nivel CHECK (nivel_actual IN ('Junior', 'Mid', 'Senior')),
    anos_experiencia        INT                 NOT NULL DEFAULT 0,
    salario_min             DECIMAL(12,2)       NULL,
    salario_max             DECIMAL(12,2)       NULL,
    moneda                  NVARCHAR(10)        NOT NULL DEFAULT 'COP',

    -- Modalidades aceptadas (separadas por coma: "Remoto,Híbrido")
    modalidades_aceptadas   NVARCHAR(100)       NOT NULL DEFAULT 'Remoto,Híbrido,Presencial',

    -- Control
    activo                  BIT                 NOT NULL DEFAULT 1,
    fecha_creacion          DATETIME            NOT NULL DEFAULT GETDATE(),
    fecha_actualizacion     DATETIME            NOT NULL DEFAULT GETDATE()
);
GO

PRINT '✓ Tabla perfil_usuario creada correctamente.';
GO
