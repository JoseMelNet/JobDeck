-- ============================================================
-- fix_campos_truncados.sql
-- Amplía a NVARCHAR(MAX) todos los campos de texto libre
-- que podrían truncarse con datos reales.
-- Ejecutar en SSMS sobre job_postings_mvp.
-- ============================================================

USE job_postings_mvp;
GO

-- ── perfil_usuario ───────────────────────────────────────────
ALTER TABLE perfil_usuario
    ALTER COLUMN direccion NVARCHAR(MAX) NULL;
GO

-- ── perfil_experiencia_laboral ───────────────────────────────
ALTER TABLE perfil_experiencia_laboral
    ALTER COLUMN descripcion_empresa NVARCHAR(MAX) NULL;
GO

-- ── perfil_proyectos ─────────────────────────────────────────
ALTER TABLE perfil_proyectos
    ALTER COLUMN stack NVARCHAR(MAX) NULL;
GO

-- ── perfil_skills ────────────────────────────────────────────
-- categoria y skill son nombres cortos, se dejan como están.

-- ── cvs_base ─────────────────────────────────────────────────
-- resumen_profesional ya es NVARCHAR(MAX), ok.

PRINT '✓ Todos los campos ampliados correctamente.';
GO
