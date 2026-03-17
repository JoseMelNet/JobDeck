-- ============================================================
-- 00_MAESTRO_ejecutar_todo.sql
-- Script maestro: crea todas las tablas nuevas en orden.
-- Ejecutar en SSMS sobre la BD job_postings_mvp.
--
-- ORDEN OBLIGATORIO (respeta dependencias entre tablas):
--   1. perfil_usuario
--   2. perfil_skills
--   3. perfil_experiencia_laboral
--   4. perfil_proyectos
--   5. perfil_educacion
--   6. perfil_cursos
--   7. perfil_certificaciones
--   8. cvs_base
--   9. vacantes_analisis
--
-- PREREQUISITO: La tabla "vacantes" debe existir.
-- ============================================================

USE job_postings_mvp;
GO

PRINT '============================================================';
PRINT 'Iniciando creación de tablas - Iteración 1';
PRINT '============================================================';
GO

-- ── 1. perfil_usuario ────────────────────────────────────────
IF OBJECT_ID('perfil_usuario', 'U') IS NOT NULL
    PRINT '⚠ perfil_usuario ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_usuario (
        id                      INT IDENTITY(1,1)   PRIMARY KEY,
        nombre                  NVARCHAR(100)       NOT NULL,
        titulo_profesional      NVARCHAR(150)       NOT NULL,
        ciudad                  NVARCHAR(100)       NULL,
        direccion               NVARCHAR(200)       NULL,
        celular                 NVARCHAR(30)        NULL,
        correo                  NVARCHAR(150)       NULL,
        perfil_linkedin         NVARCHAR(300)       NULL,
        perfil_github           NVARCHAR(300)       NULL,
        nivel_actual            NVARCHAR(20)        NOT NULL
            CONSTRAINT CK_perfil_nivel CHECK (nivel_actual IN ('Junior', 'Mid', 'Senior')),
        anos_experiencia        INT                 NOT NULL DEFAULT 0,
        salario_min             DECIMAL(12,2)       NULL,
        salario_max             DECIMAL(12,2)       NULL,
        moneda                  NVARCHAR(10)        NOT NULL DEFAULT 'COP',
        modalidades_aceptadas   NVARCHAR(100)       NOT NULL DEFAULT 'Remoto,Híbrido,Presencial',
        activo                  BIT                 NOT NULL DEFAULT 1,
        fecha_creacion          DATETIME            NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion     DATETIME            NOT NULL DEFAULT GETDATE()
    );
    PRINT '✓ perfil_usuario creada.';
END
GO

-- ── 2. perfil_skills ─────────────────────────────────────────
IF OBJECT_ID('perfil_skills', 'U') IS NOT NULL
    PRINT '⚠ perfil_skills ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_skills (
        id              INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id       INT                 NOT NULL
            CONSTRAINT FK_skills_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        categoria       NVARCHAR(100)       NOT NULL,
        skill           NVARCHAR(100)       NOT NULL,
        nivel           NVARCHAR(20)        NOT NULL,
        fecha_creacion  DATETIME            NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_perfil_skills_perfil_id ON perfil_skills(perfil_id);
    CREATE INDEX IX_perfil_skills_categoria ON perfil_skills(perfil_id, categoria);
    PRINT '✓ perfil_skills creada.';
END
GO

-- ── 3. perfil_experiencia_laboral ────────────────────────────
IF OBJECT_ID('perfil_experiencia_laboral', 'U') IS NOT NULL
    PRINT '⚠ perfil_experiencia_laboral ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_experiencia_laboral (
        id                  INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id           INT                 NOT NULL
            CONSTRAINT FK_experiencia_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        cargo               NVARCHAR(150)       NOT NULL,
        empresa             NVARCHAR(150)       NOT NULL,
        ciudad              NVARCHAR(100)       NULL,
        fecha_inicio        DATE                NOT NULL,
        fecha_fin           DATE                NULL,
        es_trabajo_actual   BIT                 NOT NULL DEFAULT 0,
        descripcion_empresa NVARCHAR(300)       NULL,
        funciones           NVARCHAR(MAX)       NULL,
        logros              NVARCHAR(MAX)       NULL,
        fecha_creacion      DATETIME            NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion DATETIME            NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_experiencia_perfil_id ON perfil_experiencia_laboral(perfil_id);
    PRINT '✓ perfil_experiencia_laboral creada.';
END
GO

-- ── 4. perfil_proyectos ──────────────────────────────────────
IF OBJECT_ID('perfil_proyectos', 'U') IS NOT NULL
    PRINT '⚠ perfil_proyectos ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_proyectos (
        id                  INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id           INT                 NOT NULL
            CONSTRAINT FK_proyectos_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        nombre              NVARCHAR(150)       NOT NULL,
        empresa             NVARCHAR(150)       NULL,
        ciudad              NVARCHAR(100)       NULL,
        fecha_inicio        DATE                NOT NULL,
        fecha_fin           DATE                NULL,
        es_proyecto_actual  BIT                 NOT NULL DEFAULT 0,
        stack               NVARCHAR(500)       NULL,
        funciones           NVARCHAR(MAX)       NULL,
        logros              NVARCHAR(MAX)       NULL,
        url_repositorio     NVARCHAR(300)       NULL,
        fecha_creacion      DATETIME            NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion DATETIME            NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_proyectos_perfil_id ON perfil_proyectos(perfil_id);
    PRINT '✓ perfil_proyectos creada.';
END
GO

-- ── 5. perfil_educacion ──────────────────────────────────────
IF OBJECT_ID('perfil_educacion', 'U') IS NOT NULL
    PRINT '⚠ perfil_educacion ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_educacion (
        id              INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id       INT                 NOT NULL
            CONSTRAINT FK_educacion_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        titulo          NVARCHAR(200)       NOT NULL,
        institucion     NVARCHAR(200)       NOT NULL,
        ciudad          NVARCHAR(100)       NULL,
        nivel           NVARCHAR(50)        NOT NULL
            CONSTRAINT CK_educacion_nivel CHECK (nivel IN (
                'Bachillerato','Técnico','Tecnólogo','Pregrado',
                'Especialización','Maestría','Doctorado','Otro'
            )),
        fecha_inicio    DATE                NOT NULL,
        fecha_fin       DATE                NULL,
        status          NVARCHAR(20)        NOT NULL DEFAULT 'Completado'
            CONSTRAINT CK_educacion_status CHECK (status IN (
                'En curso','Completado','Pausado','Abandonado'
            )),
        fecha_creacion      DATETIME        NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion DATETIME        NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_educacion_perfil_id ON perfil_educacion(perfil_id);
    PRINT '✓ perfil_educacion creada.';
END
GO

-- ── 6. perfil_cursos ─────────────────────────────────────────
IF OBJECT_ID('perfil_cursos', 'U') IS NOT NULL
    PRINT '⚠ perfil_cursos ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_cursos (
        id              INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id       INT                 NOT NULL
            CONSTRAINT FK_cursos_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        titulo          NVARCHAR(200)       NOT NULL,
        institucion     NVARCHAR(150)       NOT NULL,
        fecha_inicio    DATE                NULL,
        fecha_fin       DATE                NULL,
        status          NVARCHAR(20)        NOT NULL DEFAULT 'Completado'
            CONSTRAINT CK_cursos_status CHECK (status IN ('En curso','Completado','Pausado')),
        url_certificado NVARCHAR(300)       NULL,
        fecha_creacion      DATETIME        NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion DATETIME        NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_cursos_perfil_id ON perfil_cursos(perfil_id);
    PRINT '✓ perfil_cursos creada.';
END
GO

-- ── 7. perfil_certificaciones ────────────────────────────────
IF OBJECT_ID('perfil_certificaciones', 'U') IS NOT NULL
    PRINT '⚠ perfil_certificaciones ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE perfil_certificaciones (
        id                  INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id           INT                 NOT NULL
            CONSTRAINT FK_certificaciones_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        titulo              NVARCHAR(200)       NOT NULL,
        institucion         NVARCHAR(150)       NOT NULL,
        fecha_obtencion     DATE                NOT NULL,
        fecha_vencimiento   DATE                NULL,
        status              NVARCHAR(20)        NOT NULL DEFAULT 'Vigente'
            CONSTRAINT CK_cert_status CHECK (status IN ('Vigente','Vencido','En proceso')),
        url_certificado     NVARCHAR(300)       NULL,
        fecha_creacion          DATETIME        NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion     DATETIME        NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_certificaciones_perfil_id ON perfil_certificaciones(perfil_id);
    PRINT '✓ perfil_certificaciones creada.';
END
GO

-- ── 8. cvs_base ──────────────────────────────────────────────
IF OBJECT_ID('cvs_base', 'U') IS NOT NULL
    PRINT '⚠ cvs_base ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE cvs_base (
        id                      INT IDENTITY(1,1)   PRIMARY KEY,
        perfil_id               INT                 NOT NULL
            CONSTRAINT FK_cvs_perfil REFERENCES perfil_usuario(id) ON DELETE CASCADE,
        nombre_rol              NVARCHAR(150)       NOT NULL,
        resumen_profesional     NVARCHAR(MAX)       NOT NULL,
        experiencias_ids        NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        proyectos_ids           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        skills_ids              NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        cursos_ids              NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        certificaciones_ids     NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        educacion_ids           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        activo                  BIT                 NOT NULL DEFAULT 1,
        fecha_creacion          DATETIME            NOT NULL DEFAULT GETDATE(),
        fecha_actualizacion     DATETIME            NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_cvs_base_perfil_id ON cvs_base(perfil_id);
    PRINT '✓ cvs_base creada.';
END
GO

-- ── 9. vacantes_analisis ─────────────────────────────────────
IF OBJECT_ID('vacantes_analisis', 'U') IS NOT NULL
    PRINT '⚠ vacantes_analisis ya existe, se omite.'
ELSE
BEGIN
    CREATE TABLE vacantes_analisis (
        id                          INT IDENTITY(1,1)   PRIMARY KEY,
        vacante_id                  INT                 NOT NULL
            CONSTRAINT FK_analisis_vacante REFERENCES vacantes(id) ON DELETE CASCADE,
        perfil_id                   INT                 NOT NULL
            CONSTRAINT FK_analisis_perfil REFERENCES perfil_usuario(id),
        cv_base_id                  INT                 NULL
            CONSTRAINT FK_analisis_cv REFERENCES cvs_base(id),
        skills_requeridas           NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        skills_blandas_detectadas   NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        seniority_inferido          NVARCHAR(20)        NOT NULL DEFAULT 'No especificado'
            CONSTRAINT CK_seniority CHECK (seniority_inferido IN (
                'Junior','Mid','Senior','No especificado'
            )),
        justificacion_seniority     NVARCHAR(MAX)       NULL,
        modalidad_detectada         NVARCHAR(20)        NULL,
        salario_detectado           NVARCHAR(150)       NULL,
        idiomas_requeridos          NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        score_total                 DECIMAL(5,2)        NOT NULL DEFAULT 0,
        score_skills_tecnicas       DECIMAL(5,2)        NOT NULL DEFAULT 0,
        score_seniority             DECIMAL(5,2)        NOT NULL DEFAULT 0,
        score_modalidad             DECIMAL(5,2)        NOT NULL DEFAULT 0,
        score_idiomas               DECIMAL(5,2)        NOT NULL DEFAULT 0,
        score_skills_blandas        DECIMAL(5,2)        NOT NULL DEFAULT 0,
        semaforo                    NVARCHAR(10)        NOT NULL DEFAULT 'gris'
            CONSTRAINT CK_semaforo CHECK (semaforo IN ('verde','amarillo','rojo','gris')),
        resumen_analisis            NVARCHAR(MAX)       NULL,
        skills_match                NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        skills_gap                  NVARCHAR(MAX)       NOT NULL DEFAULT '[]',
        aspiracion_salarial_sugerida NVARCHAR(150)      NULL,
        sugerencias_cv              NVARCHAR(MAX)       NULL,
        fecha_analisis              DATETIME            NOT NULL DEFAULT GETDATE()
    );
    CREATE UNIQUE INDEX IX_vacantes_analisis_vacante_id ON vacantes_analisis(vacante_id);
    CREATE INDEX IX_vacantes_analisis_semaforo ON vacantes_analisis(semaforo);
    PRINT '✓ vacantes_analisis creada.';
END
GO

PRINT '============================================================';
PRINT 'Todas las tablas creadas correctamente.';
PRINT '============================================================';
GO
