"""
test_connection.py - Testing rápido de conexión a SQL Server
Ejecutar antes de iniciar la app para validar que todo funciona
"""

import sys
from config import CONNECTION_STRING
from database import test_connection, contar_vacantes, obtener_todas_vacantes

print("=" * 60)
print("🧪 TEST DE CONEXIÓN A SQL SERVER")
print("=" * 60)

# Test 1: Conexión básica
print("\n[1/4] Probando conexión a SQL Server...")
if test_connection():
    print("✅ Conexión exitosa")
else:
    print("❌ Error de conexión")
    print(f"\nString de conexión: {CONNECTION_STRING}")
    sys.exit(1)

# Test 2: Contar vacantes
print("\n[2/4] Contando vacantes...")
try:
    total = contar_vacantes()
    print(f"✅ Total de vacantes: {total}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Obtener todas las vacantes
print("\n[3/4] Obteniendo todas las vacantes...")
try:
    vacantes = obtener_todas_vacantes()
    if vacantes:
        print(f"✅ Se obtuvieron {len(vacantes)} vacante(s)")
        for v in vacantes[:2]:
            print(f"   - {v['empresa']} | {v['cargo']}")
    else:
        print("✅ Base de datos vacía (normal si es primera vez)")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 4: Estructura de BD
print("\n[4/4] Validando estructura de BD...")
try:
    import pyodbc

    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    # Verificar que la tabla existe
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'vacantes'
    """)

    if cursor.fetchone():
        print("✅ Tabla 'vacantes' existe y es accesible")
    else:
        print("❌ Tabla 'vacantes' no encontrada")
        print("   Ejecuta el script job_postings_mvp.sql en SSMS")
        sys.exit(1)

    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 60)
print("\n🚀 Ya puedes ejecutar: streamlit run app.py\n")