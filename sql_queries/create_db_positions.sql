-- ============================================================
-- SCRIPT: Crear Base de Datos y Tabla de Vacantes
-- MVP: Sistema de Almacenamiento de Vacantes
-- ============================================================

-- 1. Crear base de datos
CREATE DATABASE job_postings_mvp;
GO

-- 2. Usar la base de datos
USE job_postings_mvp;
GO

-- 3. Crear tabla de vacantes
CREATE TABLE vacantes (
    id INT PRIMARY KEY IDENTITY(1,1),
    empresa NVARCHAR(255) NOT NULL,
    cargo NVARCHAR(255) NOT NULL,
    modalidad NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(MAX) NOT NULL,
    fecha_registro DATETIME DEFAULT GETDATE(),
    CONSTRAINT CHK_modalidad CHECK (modalidad IN ('Remoto', 'Presencial', 'Híbrido'))
);

-- 4. Crear índices para búsquedas rápidas
CREATE INDEX IDX_empresa ON vacantes(empresa);
CREATE INDEX IDX_cargo ON vacantes(cargo);
CREATE INDEX IDX_fecha ON vacantes(fecha_registro DESC);

-- 5. Verificar creación
SELECT * FROM vacantes;