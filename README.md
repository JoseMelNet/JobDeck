# 📋 MVP: Sistema de Almacenamiento de Vacantes

Sistema simple y funcional para registrar y almacenar vacantes en SQL Server.

## 🎯 Características

✅ Formulario para capturar vacantes (Empresa, Cargo, Modalidad, Descripción)  
✅ Preview antes de guardar + confirmación  
✅ Visualización de todas las vacantes registradas  
✅ Opción de eliminar vacantes  
✅ Almacenamiento en SQL Server local  
✅ Interfaz en Streamlit (bonita y funcional)

---

## ⚙️ Requisitos Previos

- **Windows** (SQL Server)
- **Python 3.8+** instalado
- **SQL Server Developer Edition** instalado (gratuito)
- **SSMS** (SQL Server Management Studio) instalado

> Si no tienes SQL Server, descárgalo desde:  
> https://www.microsoft.com/sql-server/sql-server-downloads

---

## 🚀 Instalación (15 minutos)

### Paso 1: Crear la Base de Datos

1. Abre **SQL Server Management Studio (SSMS)**
2. Conéctate a tu instancia local (ej: `localhost\SQLEXPRESS`)
3. Abre un **New Query**
4. **Copia y pega** todo el contenido de `job_postings_mvp.sql`
5. Presiona **Execute** (F5)

✅ Deberías ver un mensaje de éxito. La BD `job_postings_mvp` está creada.

### Paso 2: Configurar Variables de Entorno

1. En la carpeta del proyecto, **copia** `.env.example` a `.env`
   ```bash
   copy .env.example .env
   ```

2. **Abre `.env`** con un editor de texto y completa tus credenciales:
   ```
   DB_SERVER=localhost\SQLEXPRESS
   DB_DATABASE=job_postings_mvp
   DB_USER=sa
   DB_PASSWORD=tu_contraseña_sql_server
   ```

### Paso 3: Instalar Dependencias Python

```bash
# Abre PowerShell o CMD en la carpeta del proyecto

# Crear entorno virtual
python -m venv venv

# Activar (Windows - PowerShell)
venv\Scripts\Activate.ps1

# O en CMD:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación

```bash
# Con venv activado
streamlit run app.py
```

✅ Se abrirá automáticamente en tu navegador (http://localhost:8501)

---

## 💡 Cómo Usar

### Pestaña 1: Registrar Vacante

1. **Completa el formulario:**
   - Empresa: nombre de la empresa
   - Cargo: posición ofrecida
   - Modalidad: Remoto / Presencial / Híbrido
   - Descripción: pega toda la descripción de la vacante

2. **Click en "Ver Preview"**
   - Se mostrará una vista previa de lo que vas a guardar

3. **Click en "Confirmar y Guardar"**
   - Se guardará en la BD
   - Verás un mensaje de éxito
   - El contador de vacantes se actualiza automáticamente

### Pestaña 2: Mis Vacantes

- Ves **todas las vacantes registradas**
- Cada una muestra: empresa, cargo, modalidad, descripción resumida
- **Puedes eliminar** una vacante con el botón 🗑️

---

## 🛠️ Estructura del Proyecto

```
job_postings_mvp/
├── app.py                      # Aplicación Streamlit (MAIN)
├── database.py                 # CRUD: funciones de BD
├── config.py                   # Configuración y credenciales
├── requirements.txt            # Dependencias Python
├── job_postings_mvp.sql        # Script para crear BD
├── .env.example                # Template de variables de entorno
├── .env                        # Variables de entorno (NO comitear)
└── README.md                   # Este archivo
```

---

## 🔧 Solución de Problemas

### ❌ "Error: No hay conexión a SQL Server"

**Causa:** Credenciales incorrectas o SQL Server no está corriendo.

**Solución:**
1. Verifica que SQL Server esté ejecutándose (Services en Windows)
2. Abre SSMS y prueba conectar manualmente
3. Verifica credenciales en `.env`
4. Recarga la app (F5 en el navegador)

### ❌ "ODBC Driver 17 for SQL Server not found"

**Causa:** Driver ODBC no instalado.

**Solución:**
```bash
# Instala el driver ODBC
pip install pyodbc --upgrade
```

O descárgalo manualmente:  
https://www.microsoft.com/download/details.aspx?id=56567

### ❌ "Table vacantes doesn't exist"

**Causa:** No ejecutaste el script SQL.

**Solución:**
1. Abre SSMS
2. Ejecuta el script `job_postings_mvp.sql` nuevamente
3. Verifica que la tabla existe: `SELECT * FROM vacantes`

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Registrar una vacante de LinkedIn

```
Empresa: Google
Cargo: Data Analyst
Modalidad: Remoto
Descripción: [pega todo el texto de la vacante aquí]
```

### Ejemplo 2: Vacante de Indeed

```
Empresa: Microsoft
Cargo: BI Analyst
Modalidad: Híbrido
Descripción: [copia y pega la descripción completa]
```

---

## 🚀 Próximas Mejoras

- [ ] Agregar búsqueda/filtro en "Mis Vacantes"
- [ ] Exportar a CSV/Excel
- [ ] Agregar más campos (salario, link, seniority)
- [ ] Análisis con IA (validar skills requeridos)
- [ ] Scoring automático de afinidad
- [ ] Generación de CV adaptado por vacante

---

## 📧 Soporte

Si tienes problemas:

1. Verifica la consola de errores (PowerShell/CMD)
2. Revisa que SQL Server esté corriendo
3. Intenta conectar a SSMS manualmente
4. Recarga la app (`Ctrl+C` y vuelve a ejecutar)

---

## 📄 Licencia

Proyecto personal. Uso libre.

---

**¡Listo para usar! Ejecuta `streamlit run app.py` y comienza a registrar vacantes.** 🎉