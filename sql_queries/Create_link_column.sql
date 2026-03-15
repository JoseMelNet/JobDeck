-- ============================================================
-- Script para agregar columna LINK a tabla vacantes
-- Ejecutar en SSMS en la BD: job_postings_mvp
-- ============================================================

USE job_postings_mvp;
GO

-- Verificar si la columna ya existe
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
              WHERE TABLE_NAME = 'vacantes' AND COLUMN_NAME = 'link')
BEGIN
    -- Agregar la columna link
    ALTER TABLE vacantes
    ADD link NVARCHAR(500) NULL;
    
    PRINT '✓ Columna link agregada exitosamente';
END
ELSE
BEGIN
    PRINT '⚠️ Columna link ya existe';
END

GO

-- Verificar estructura de tabla
SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'vacantes'
ORDER BY ORDINAL_POSITION;
GO

SELECT * FROM dbo.vacantes;