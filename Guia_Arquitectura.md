# 📐 GUÍA DEFINITIVA: ARQUITECTURA PROFESIONAL EN PYTHON (v2.0)

**Versión:** 2.0 (Mejorada)  
**Última actualización:** Marzo 2026  
**Propósito:** Referencia universal para arquitectura profesional en Python  
**Aplicable a:** Cualquier tamaño de proyecto (MVP, startup, enterprise)

---

## 📑 TABLA DE CONTENIDOS

1. [Propósito de Esta Guía](#propósito-de-esta-guía)
2. [Qué Logra una Arquitectura Profesional](#qué-logra-una-arquitectura-profesional)
3. [Principios Fundamentales](#principios-fundamentales)
4. [Anti-Patrones a Detectar Temprano](#anti-patrones-a-detectar-temprano)
5. [Árbol de Decisión Arquitectónico](#árbol-de-decisión-arquitectónico)
6. [Arquitectura en Capas](#arquitectura-en-capas)
7. [Estructura de Directorios](#estructura-de-directorios)
8. [Plantillas por Tipo de Proyecto](#plantillas-por-tipo-de-proyecto)
9. [Patrones de Diseño](#patrones-de-diseño)
10. [Manejo de Errores y Excepciones](#manejo-de-errores-y-excepciones)
11. [Logging y Observabilidad](#logging-y-observabilidad)
12. [Testing](#testing)
13. [Inyección de Dependencias](#inyección-de-dependencias)
14. [Naming y Organización](#naming-y-organización)
15. [Tooling Mínimo](#tooling-mínimo)
16. [Documentación Obligatoria](#documentación-obligatoria)
17. [Seguridad Básica](#seguridad-básica)
18. [Cuándo Refactorizar](#cuándo-refactorizar)
19. [Checklists](#checklists)
20. [Reglas de Oro](#reglas-de-oro)

---

## PROPÓSITO DE ESTA GUÍA

Este documento sirve como marco general para diseñar arquitecturas de proyectos profesionales en Python. **No está ligado a un proyecto particular** ni a tecnologías específicas de base de datos, interfaz o despliegue.

### Objetivos

✅ Ayudarte a tomar **decisiones mejores desde el inicio**  
✅ Evitar **errores comunes y costosos**:
- Meter demasiada lógica en un solo archivo
- Acoplar la UI con la base de datos
- Duplicar reglas de negocio
- Dispersar configuración y constantes
- Crear código difícil de testear
- Escalar sobre una base desordenada

✅ Buscar **criterio técnico útil**, no "arquitectura perfecta"  
✅ Que el proyecto siga siendo **modificable, entendible y mantenible** cuando crezca

---

## QUÉ LOGRA UNA ARQUITECTURA PROFESIONAL

Una arquitectura profesional debe permitir:

1. **Cambiar una parte sin romper el resto**
   - Los módulos están desacoplados
   - Los cambios locales no crean cascadas

2. **Entender el sistema sin leer todo el repo**
   - Estructura clara y predecible
   - Responsabilidades obvias

3. **Probar la lógica sin depender siempre de infraestructura real**
   - Tests rápidos y aislados
   - Mocks inyectables

4. **Incorporar nuevas funcionalidades sin duplicar código**
   - Single source of truth
   - Reutilización clara

5. **Integrar nuevas tecnologías sin rehacer la aplicación**
   - Adaptadores y abstracción
   - Bajo acoplamiento

6. **Trabajar en equipo sin que todo quede en la cabeza del autor**
   - Documentación clara
   - Patrones consistentes

---

**⚠️ Si el proyecto da miedo tocarlo, la arquitectura ya está fallando.**

---

## PRINCIPIOS FUNDAMENTALES

### 1. Responsabilidad Única (SRP)

Cada módulo, clase o función debe tener **una razón clara para cambiar**.

```python
# ❌ MAL: Una clase hace todo
class DataManager:
    def fetch_data(self): pass           # Acceso a datos
    def validate_data(self): pass         # Validación
    def transform_data(self): pass        # Transformación
    def save_to_db(self): pass           # Persistencia
    def send_notification(self): pass     # Notificación
    def log_activity(self): pass         # Logging

# ✅ BIEN: Cada clase tiene una responsabilidad
class DataFetcher:
    def fetch(self): pass

class DataValidator:
    def validate(self): pass

class DataTransformer:
    def transform(self): pass

class DataRepository:
    def save(self): pass

class NotificationService:
    def notify(self): pass
```

**Mala señal:** Un archivo valida datos, consulta BD, transforma resultados, arma respuestas y además maneja UI.  
**Buena señal:** Cada capa hace su parte y nada más.

---

### 2. Separación de Preocupaciones

Interfaz, negocio, persistencia, integración y configuración **no deben estar mezclados**.

```python
# ❌ MAL
def register_user(request):
    name = request.get('name')
    email = request.get('email')
    
    # Validación en controller
    if not email.endswith('@'):
        return {"error": "invalid"}
    
    # SQL directo en endpoint
    db.execute("INSERT INTO users...")
    
    # Lógica de integración aquí
    requests.post("https://api...")
    
    return {"ok": True}

# ✅ BIEN
# En presentación (controller/endpoint)
def register_user(request):
    user_data = request.dict()
    result = user_service.register(user_data)
    return result

# En servicios (lógica)
class UserService:
    def register(self, user_data):
        user = User(**user_data)
        self.validator.validate(user)
        saved_user = self.repository.save(user)
        self.notification_client.send_welcome(saved_user.email)
        return saved_user

# En repositorio (persistencia)
class UserRepository:
    def save(self, user):
        # SQL aquí
        pass

# En cliente (integración)
class NotificationClient:
    def send_welcome(self, email):
        # HTTP aquí
        pass
```

---

### 3. Bajo Acoplamiento

Un cambio local no debería provocar una cascada de cambios en veinte archivos.

```python
# ❌ MAL: Acoplado
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Acoplado a PostgreSQL
        self.payment = PayPalPayment()  # Acoplado a PayPal
        self.email = GmailService()     # Acoplado a Gmail

# ✅ BIEN: Desacoplado
class OrderService:
    def __init__(self, 
                 database: DatabaseInterface,
                 payment: PaymentInterface,
                 email: EmailInterface):
        self.db = database
        self.payment = payment
        self.email = email

# Ahora puedes cambiar implementaciones
service = OrderService(
    PostgresDatabase(),
    PayPalPayment(),
    GmailService()
)

# O diferentes implementaciones
service = OrderService(
    MongoDatabase(),
    StripePayment(),
    SendgridService()
)
```

---

### 4. Alta Cohesión

Las piezas que viven juntas deben estar relacionadas por **responsabilidad real**, no por comodidad momentánea.

```python
# ❌ MAL: Baja cohesión
class utils.py:
    def calculate_tax(): pass
    def send_email(): pass
    def validate_date(): pass
    def hash_password(): pass
    def generate_report(): pass
    # ... 50 funciones sin relación

# ✅ BIEN: Alta cohesión
class tax_calculator.py:
    def calculate(): pass

class email_service.py:
    def send(): pass

class date_validator.py:
    def validate(): pass

class security.py:
    def hash_password(): pass

class reporting.py:
    def generate_report(): pass
```

---

### 5. Single Source of Truth

Las **reglas de negocio, enums, límites, formatos y constantes** no deben existir repetidos en múltiples archivos.

```python
# ❌ MAL: Constantes dispersas
# En models.py
class User:
    MAX_EMAIL_LENGTH = 255
    MIN_PASSWORD_LENGTH = 8

# En validators.py
def validate_email(email):
    if len(email) > 255:  # Repetido
        raise Error()

# En tests
def test_user():
    assert user.email_length <= 255  # Repetido nuevamente

# ✅ BIEN: Single source of truth
# En config/constants.py
class UserConstraints:
    MAX_EMAIL_LENGTH = 255
    MIN_PASSWORD_LENGTH = 8
    VALID_ROLES = ["admin", "user", "guest"]

# En models.py
from config.constants import UserConstraints

class User:
    MAX_EMAIL_LENGTH = UserConstraints.MAX_EMAIL_LENGTH
    MIN_PASSWORD_LENGTH = UserConstraints.MIN_PASSWORD_LENGTH

# En validators.py
from config.constants import UserConstraints

def validate_email(email):
    if len(email) > UserConstraints.MAX_EMAIL_LENGTH:
        raise Error()

# En tests
def test_user():
    assert user.email_length <= UserConstraints.MAX_EMAIL_LENGTH
```

---

### 6. Testabilidad

La **lógica importante debe poder probarse en aislamiento**.

```python
# ❌ MAL: Difícil de testear
class OrderService:
    def process_order(self, order_id):
        db = create_connection()  # Requiere BD real
        order = db.query(f"SELECT * FROM orders WHERE id={order_id}")
        
        response = requests.post("https://api.payment.com/charge")  # Requiere API real
        
        if response.status_code == 200:
            db.execute(f"UPDATE orders SET status='paid'...")
        
        return order

# ✅ BIEN: Fácil de testear
class OrderService:
    def __init__(self, order_repo, payment_client):
        self.order_repo = order_repo
        self.payment_client = payment_client
    
    def process_order(self, order_id):
        order = self.order_repo.get_by_id(order_id)
        payment_result = self.payment_client.charge(order.amount)
        
        if payment_result.success:
            self.order_repo.update_status(order_id, "paid")
        
        return order

# En tests
class TestOrderService:
    def test_process_order(self):
        mock_repo = Mock()
        mock_payment = Mock()
        
        service = OrderService(mock_repo, mock_payment)
        result = service.process_order(1)
        
        assert result is not None
        mock_repo.update_status.assert_called_once()
```

---

### 7. Evolución Pragmática

La arquitectura debe dejar **crecer el proyecto sin obligarte a reescribirlo todo**.

```python
# MVP: Simple
project/
├── main.py
├── config.py
└── helpers.py

# Cuando crezca: Modularizar
project/
├── app/
│   ├── main.py
│   ├── services/
│   ├── repositories/
│   └── models/
└── tests/

# Cuando sea grande: Capas completas
project/
├── app/
│   ├── domain/
│   ├── services/
│   ├── repositories/
│   ├── infrastructure/
│   └── interfaces/
└── tests/
```

---

### 8. Simplicidad con Criterio

**No diseñes para un sistema que no existe todavía.** Diseña para el problema actual, dejando espacio razonable para crecer.

```python
# ❌ MAL: Sobrediseño
# Para un sistema de tareas simple
class TaskEventBus:
    def subscribe(self): pass
    def publish(self): pass

class TaskAggregate:
    def apply_event(self): pass
    def get_uncommitted_events(self): pass

class TaskProjection:
    def handle_task_created(self): pass

# Si no necesitas event sourcing, es complejidad innecesaria

# ✅ BIEN: Empezar simple
class TaskService:
    def create_task(self, title):
        task = Task(title)
        self.repository.save(task)
        return task

# Agregar complejidad cuando realmente la necesites
```

---

## ANTI-PATRONES A DETECTAR TEMPRANO

Estos son problemas frecuentes y **costosos**:

### 1. Archivo "Todopoderoso"

Un `app.py`, `database.py`, `utils.py` o `main.py` con **cientos de líneas** y múltiples responsabilidades.

**Señales de alerta:**
- Archivo > 500 líneas
- Más de 3-4 imports de módulos muy diferentes
- Funciones sin relación aparente
- Cambios frecuentes por razones muy distintas

**Solución:** Dividir en módulos especializados

---

### 2. UI Hablando Directo con la Base de Datos

Un endpoint, pantalla o script ejecutando **SQL directo**.

```python
# ❌ ANTI-PATRÓN
@app.post("/users")
def create_user(request):
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
               (request.name, request.email))
    return {"ok": True}

# ✅ CORRECTO
@app.post("/users")
def create_user(request):
    user = user_service.create_user(request.dict())
    return user.to_dict()
```

---

### 3. Reglas de Negocio Dispersas

La misma validación escrita en **UI, service, DAO y test**.

```python
# ❌ ANTI-PATRÓN: Validación repetida
# En UI
if len(email) < 5:
    error = "Email too short"

# En Service
if len(email) < 5:
    raise ValidationError()

# En DAO
if len(email) < 5:
    return False

# ✅ CORRECTO: Una sola fuente
class EmailValidator:
    MIN_LENGTH = 5
    
    def validate(self, email):
        if len(email) < self.MIN_LENGTH:
            raise ValidationError(f"Email must be at least {self.MIN_LENGTH} chars")

# Usarla en todos lados
validator = EmailValidator()
validator.validate(email)
```

---

### 4. Constantes Mágicas

Strings, estados, IDs, nombres de columnas o límites **repetidos por todas partes**.

```python
# ❌ ANTI-PATRÓN
def process_order(order):
    if order.status == "pending":
        # ...
    elif order.status == "processing":
        # ...
    elif order.status == "shipped":
        # ...

def validate_order(order):
    if order.status not in ["pending", "processing", "shipped", "delivered"]:
        # ...

# ✅ CORRECTO: Enums
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

def process_order(order):
    if order.status == OrderStatus.PENDING:
        # ...

def validate_order(order):
    if order.status not in OrderStatus:
        # ...
```

---

### 5. Infraestructura Filtrada en Todo el Sistema

`os.getenv()`, `requests`, `pyodbc`, `sqlalchemy`, rutas locales y **detalles de nube** metidos en múltiples módulos.

```python
# ❌ ANTI-PATRÓN
# En user_service.py
def get_user(user_id):
    import requests
    response = requests.get(f"http://api.external.com/users/{user_id}")
    return response.json()

# En email_sender.py
import os
def send_email(recipient):
    api_key = os.getenv("SENDGRID_KEY")
    requests.post("https://api.sendgrid.com/", headers={"key": api_key})

# ✅ CORRECTO: Encapsular
# En infrastructure/clients/external_api_client.py
class ExternalAPIClient:
    def __init__(self):
        self.base_url = "http://api.external.com"
    
    def get_user(self, user_id):
        import requests
        response = requests.get(f"{self.base_url}/users/{user_id}")
        return response.json()

# En infrastructure/email/sendgrid_service.py
import os
class SendgridEmailService:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_KEY")
    
    def send(self, recipient, subject, body):
        import requests
        requests.post("https://api.sendgrid.com/", 
                     headers={"key": self.api_key})

# En services
from infrastructure.clients import ExternalAPIClient
from infrastructure.email import SendgridEmailService

class UserService:
    def __init__(self, api_client, email_service):
        self.api_client = api_client
        self.email_service = email_service
```

---

### 6. Manejo de Errores Improvisado

`try/except` copiados por todo lado, `except: pass`, errores tragados o **mensajes ambiguos**.

```python
# ❌ ANTI-PATRÓN
def fetch_user(user_id):
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except:
        pass  # ¿Qué error? ¿Dónde? ¿Por qué?

def create_order(order_data):
    try:
        order = Order(**order_data)
        db.save(order)
        return order
    except Exception as e:
        return {"error": str(e)}  # Mensaje genérico

# ✅ CORRECTO: Excepciones propias y manejo explícito
class UserNotFoundError(Exception):
    pass

class InvalidOrderError(Exception):
    pass

def fetch_user(user_id):
    try:
        result = repository.get_by_id(user_id)
        if not result:
            raise UserNotFoundError(f"User {user_id} not found")
        return result
    except RepositoryError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise
    except UserNotFoundError:
        raise

def create_order(order_data):
    try:
        order = Order(**order_data)
        if not order.is_valid():
            raise InvalidOrderError("Order validation failed")
        repository.save(order)
        return order
    except InvalidOrderError as e:
        logger.warning(f"Invalid order: {e}")
        raise
```

---

### 7. Tests Dependientes de Entorno Real

Tests que exigen **BD real, API real o archivos manuales** para siquiera ejecutarse.

```python
# ❌ ANTI-PATRÓN
def test_user_creation():
    # Requiere BD real, servidor real, etc
    db = connect_to_production_database()
    response = requests.post("https://api.real.com/users")
    assert response.status_code == 200

# ✅ CORRECTO: Usar mocks
def test_user_creation():
    mock_repo = Mock()
    mock_repo.save.return_value = User(id=1, name="John")
    
    service = UserService(mock_repo)
    result = service.create_user({"name": "John"})
    
    assert result.id == 1
    mock_repo.save.assert_called_once()
```

---

### 8. Scripts Paralelos que Reimplementan Lógica

Código duplicado en notebooks, scripts, jobs, endpoints y módulos operativos.

```python
# ❌ ANTI-PATRÓN
# En app.py
def process_user(user_data):
    user = User(**user_data)
    if not user.email:
        raise ValidationError()
    repository.save(user)

# En scripts/bulk_import.py
def import_users(csv_file):
    for row in csv.reader(csv_file):
        user = User(**row)
        if not user.email:
            print("Skip")
            continue
        db.execute("INSERT...")  # SQL direto novamente

# Em cron_job.py
def daily_cleanup():
    for user_id in get_old_users():
        user = User(id=user_id)
        if not user.email:  # Validação repetida
            continue

# ✅ CORRECTO: Reutilizar services
from services import UserService

# Em app.py
user_service = UserService(repository, validator)

@app.post("/users")
def create_user(request):
    return user_service.create_user(request.dict())

# Em scripts/bulk_import.py
from services import UserService

def import_users(csv_file):
    for row in csv.reader(csv_file):
        try:
            user = user_service.create_user(row)
            print(f"Created {user.id}")
        except ValidationError:
            print("Skip")

# Em cron_job.py
from services import UserService

def daily_cleanup():
    for user_id in get_old_users():
        try:
            user_service.delete_user(user_id)
        except UserNotFoundError:
            continue
```

---

## ÁRBOL DE DECISIÓN ARQUITECTÓNICO

Úsalo **antes de arrancar un repo** para definir tu estructura:

### Pregunta 1: ¿Es un script desechable o un proyecto que crecerá?

- **Si es desechable:** Estructura simple (main.py + helpers.py)
- **Si crecerá:** Separa capas desde temprano

### Pregunta 2: ¿Hay lógica de negocio real?

- **Si sí:** Crea `services/` o `use_cases/` para orquestar
- **Si no:** Quizá basta una capa delgada

### Pregunta 3: ¿Hay persistencia o integraciones?

- **Si sí:** Encapsula acceso en `repositories/`, `dao/`, `gateways/` o `clients/`
- **Si no:** Mantén el proyecto más simple

### Pregunta 4: ¿Habrá múltiples interfaces?

Ejemplo: API + scripts + dashboard + jobs

- **Si sí:** Desacopla la lógica para que cada interfaz consuma la misma capa de servicios

### Pregunta 5: ¿Necesitas validación fuerte de entrada/salida?

- **Si sí:** Considera Pydantic o dataclasses con validación
- **Si no:** Dataclasses básicos pueden ser suficientes

### Pregunta 6: ¿La base de datos cambiará con frecuencia?

- **Si sí:** Usa migraciones versionadas y diseño explícito del acceso a datos
- **Si no:** SQL puro o ORM según preferencia

### Pregunta 7: ¿Es probable que entren más personas al proyecto?

- **Si sí:** La documentación y consistencia dejan de ser opcionales
- **Si no:** Puedes ser más flexible

---

## ARQUITECTURA EN CAPAS

### Modelo de 3 Capas (Recomendado para MVPs)

```
┌──────────────────────────────────────────┐
│     PRESENTATION LAYER (UI/API)          │
│ - Manejo de requests/responses            │
│ - Validación superficial de bordes        │
│ - NO: lógica de negocio                   │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│   BUSINESS LOGIC LAYER (Services)        │
│ - Lógica de negocio                      │
│ - Validaciones complejas                 │
│ - Orqueración                            │
│ - NO: SQL directo                        │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│    DATA ACCESS LAYER (DAOs/Repos)        │
│ - Queries SQL                            │
│ - Manejo de conexiones                   │
│ - Mapeo ORM                              │
│ - NO: lógica de negocio                  │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│       DATABASE (SQL Server/Postgres)     │
│ - Tablas, índices, constraints            │
└──────────────────────────────────────────┘
```

### Responsabilidades por Capa

#### Capa de Presentación

**Hace:**
- Recibir datos (request, input, command)
- Validación superficial de borde
- Llamar servicios o casos de uso
- Devolver respuesta formateada

**No hace:**
- Reglas de negocio complejas
- SQL directo
- Manejo de sesiones de BD
- Lógica de integración profunda

```python
# En API
@app.post("/users")
def register_user(request: UserCreate):
    # Validación superficial (framework)
    result = user_service.register(request.dict())
    
    if result['success']:
        return {"id": result['id']}
    else:
        return {"error": result['message']}, 400
```

---

#### Capa de Lógica de Negocio (Services)

**Hace:**
- Orquestar procesos
- Aplicar reglas de negocio
- Llamar repositorios/gateways
- Coordinar varias dependencias
- Decidir el flujo del caso de uso

**No hace:**
- Render de UI
- Detalles técnicos de framework
- Consultas dispersas de infraestructura

```python
# En service
class UserService:
    def register(self, user_data):
        # Validación de negocio
        if self.user_repo.exists_by_email(user_data['email']):
            return {'success': False, 'message': 'Email exists'}
        
        # Crear y guardar
        user = User(**user_data)
        saved_user = self.user_repo.save(user)
        
        # Notificación
        self.email_service.send_welcome(saved_user.email)
        
        return {'success': True, 'id': saved_user.id}
```

---

#### Capa de Acceso a Datos (DAOs/Repositories)

**Hace:**
- Queries SQL
- Manejo de conexiones
- Mapeo ORM
- Transacciones

**No hace:**
- Lógica de negocio
- Decisiones de aplicación

```python
# En repository
class UserRepository:
    def save(self, user):
        query = "INSERT INTO users (name, email) VALUES (?, ?)"
        cursor, conn = self._execute(query, (user.name, user.email))
        user_id = cursor.lastrowid
        self._close(cursor, conn, commit=True)
        return user_id
    
    def exists_by_email(self, email):
        query = "SELECT COUNT(*) FROM users WHERE email = ?"
        result = self.db.fetch_one(query, (email,))
        return result[0] > 0
```

---

### Modelo de 4+ Capas (Para Proyectos Grandes)

```
Presentation
    ↓
Controllers/Handlers
    ↓
Models (Domain Objects)
    ↓
Services (Business Logic)
    ↓
Repositories (Advanced Data Access)
    ↓
Infrastructure (External Services)
    ↓
Database
```

---

## ESTRUCTURA DE DIRECTORIOS

### Estructura General Recomendada

```
project/
│
├── 📁 app/                          (Código principal)
│   ├── __init__.py
│   ├── main.py                      (Punto de entrada)
│   │
│   ├── 📁 config/                   (Configuración)
│   │   ├── __init__.py
│   │   ├── settings.py              (Unified settings)
│   │   └── constants.py             (Constantes)
│   │
│   ├── 📁 domain/                   (Modelos de dominio)
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── enums/
│   │   └── value_objects/
│   │
│   ├── 📁 services/                 (Lógica de negocio)
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── order_service.py
│   │   └── shared_service.py
│   │
│   ├── 📁 repositories/             (Acceso a datos)
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── order_repository.py
│   │   └── base_repository.py
│   │
│   ├── 📁 infrastructure/           (Servicios externos)
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── migrations.py
│   │   ├── clients/
│   │   │   ├── payment_client.py
│   │   │   └── email_client.py
│   │   ├── storage/
│   │   └── logging/
│   │
│   ├── 📁 interfaces/               (Puntos de entrada)
│   │   ├── __init__.py
│   │   ├── api/                     (REST API, si aplica)
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── dependencies/
│   │   ├── cli/                     (CLI, si aplica)
│   │   └── ui/                      (Web UI, si aplica)
│   │
│   ├── 📁 utils/                    (Utilidades)
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── formatters.py
│   │   ├── decorators.py
│   │   └── helpers.py
│   │
│   └── 📁 exceptions/               (Excepciones propias)
│       ├── __init__.py
│       ├── database.py
│       ├── validation.py
│       └── business.py
│
├── 📁 tests/                        (Suite de tests)
│   ├── __init__.py
│   ├── conftest.py                  (Pytest fixtures)
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── test_repository_integration.py
│   │   └── test_service_integration.py
│   └── e2e/
│       └── test_workflows.py
│
├── 📁 docs/                         (Documentación)
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── decisions/                   (ADRs)
│   │   ├── 0001-choice-of-framework.md
│   │   └── 0002-database-strategy.md
│   └── runbooks/
│       └── deployment.md
│
├── 📁 sql/                          (Scripts de BD)
│   ├── schema/
│   │   └── 001_initial_schema.sql
│   ├── migrations/
│   │   ├── 001_create_users.sql
│   │   └── 002_add_orders.sql
│   └── seed_data.sql
│
├── 📁 scripts/                      (Scripts operativos)
│   ├── __init__.py
│   ├── create_db.py
│   ├── seed_db.py
│   └── migrate.py
│
├── .env.example                     (Template de env)
├── .env                             (Local - GITIGNORED)
├── .gitignore
├── .github/
│   └── workflows/                   (CI/CD)
│       └── tests.yml
├── pyproject.toml / setup.py        (Configuración del paquete)
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

---

## PLANTILLAS POR TIPO DE PROYECTO

### 1. Script Profesional Pequeño

Úsalo para automatizaciones simples o herramientas internas de **baja complejidad**.

```
project/
├── main.py
├── config.py
├── helpers.py
├── tests/
├── pyproject.toml
└── README.md
```

**Cuándo basta:**
- Una sola responsabilidad
- Poca lógica
- Sin múltiples integraciones complejas
- Bajo riesgo de crecimiento

**Cuándo ya no basta:**
- Aparecen varios flujos
- Múltiples fuentes de datos
- Lógica de validación repetida
- Varios comandos o múltiples salidas

---

### 2. Aplicación de Negocio Mediana

```
project/
├── app/
│   ├── main.py
│   ├── config/
│   ├── domain/
│   ├── services/
│   ├── repositories/
│   ├── infrastructure/
│   ├── interfaces/
│   └── utils/
├── tests/
├── docs/
└── pyproject.toml
```

Úsala cuando:
- Habrá mantenimiento
- Varias funcionalidades
- Persistencia o integraciones
- Interés real en escalar ordenadamente

---

### 3. API REST (FastAPI/Flask)

```
project/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routers/
│   │   │   ├── users.py
│   │   │   └── orders.py
│   │   ├── schemas/
│   │   ├── dependencies/
│   │   └── middleware/
│   ├── services/
│   ├── repositories/
│   ├── domain/
│   ├── infrastructure/
│   └── config/
├── tests/
├── docs/
└── pyproject.toml
```

---

### 4. Aplicación Web (Django/Fastapi + Frontend)

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── domain/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── infrastructure/
│   │   └── api/
│   └── tests/
├── frontend/
│   ├── src/
│   └── public/
├── docs/
└── pyproject.toml
```

---

### 5. Aplicación Streamlit/CLI

```
project/
├── app/
│   ├── main.py
│   ├── config/
│   ├── domain/
│   ├── services/
│   ├── repositories/
│   ├── infrastructure/
│   ├── ui/
│   │   ├── pages/
│   │   └── components/
│   └── utils/
├── tests/
├── docs/
└── pyproject.toml
```

---

## PATRONES DE DISEÑO

### 1. Singleton Pattern

Cuándo usar: Conexión BD, configuración global, logger

```python
class DatabaseConnection:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.connection = self._create_connection()
        self._initialized = True

# Uso
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # Misma instancia
```

---

### 2. Repository/DAO Pattern

Abstrae acceso a datos para facilitar testing y cambio de implementación.

```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def save(self, user) -> int:
        pass
    
    @abstractmethod
    def get_by_id(self, user_id) -> User:
        pass
    
    @abstractmethod
    def get_all(self) -> List[User]:
        pass

class SQLUserRepository(UserRepository):
    def save(self, user):
        # SQL implementation
        pass

class MongoUserRepository(UserRepository):
    def save(self, user):
        # MongoDB implementation
        pass

# Intercambiable
repo = SQLUserRepository() if use_sql else MongoUserRepository()
```

---

### 3. Adapter Pattern

Aísla servicios externos o librerías concretas.

```python
from abc import ABC, abstractmethod

class EmailClient(ABC):
    @abstractmethod
    def send(self, to, subject, body): pass

class GmailEmailClient(EmailClient):
    def send(self, to, subject, body):
        # Gmail implementation
        pass

class SendgridEmailClient(EmailClient):
    def send(self, to, subject, body):
        # Sendgrid implementation
        pass

# En service
class NotificationService:
    def __init__(self, email_client: EmailClient):
        self.email = email_client
    
    def notify_user(self, user_email):
        self.email.send(user_email, "Hello", "Welcome!")
```

---

### 4. Factory Pattern

Construir objetos complejos o dependencias de forma controlada.

```python
class PaymentGatewayFactory:
    @staticmethod
    def create(gateway_type: str):
        if gateway_type == "stripe":
            return StripePayment()
        elif gateway_type == "paypal":
            return PayPalPayment()
        else:
            raise ValueError(f"Unknown gateway: {gateway_type}")

# Uso
gateway = PaymentGatewayFactory.create(config.PAYMENT_GATEWAY)
```

---

### 5. Strategy Pattern

Variantes intercambiables de comportamiento.

```python
from abc import ABC, abstractmethod

class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, data) -> bool:
        pass

class StrictValidation(ValidationStrategy):
    def validate(self, data):
        # Strict rules
        pass

class LenientValidation(ValidationStrategy):
    def validate(self, data):
        # Lenient rules
        pass

# Usar estrategia diferente según contexto
validator = StrictValidation() if is_production else LenientValidation()
```

---

### 6. Dependency Injection

Desacoplar dependencias para facilitar testing y cambio.

```python
# Sin DI - Acoplado
class UserService:
    def __init__(self):
        self.repo = UserRepository()  # Acoplado
        self.email = EmailService()   # Acoplado

# Con DI - Desacoplado
class UserService:
    def __init__(self, repo: UserRepository, email: EmailService):
        self.repo = repo
        self.email = email

# En tests
mock_repo = Mock()
mock_email = Mock()
service = UserService(mock_repo, mock_email)
```

---

## MANEJO DE ERRORES Y EXCEPCIONES

### Excepciones Propias

Define excepciones que reflejen tu dominio de negocio:

```python
# En exceptions/
class ApplicationError(Exception):
    """Base para errores de aplicación"""
    pass

class ValidationError(ApplicationError):
    """Error de validación de datos"""
    pass

class UserNotFoundError(ApplicationError):
    """Usuario no encontrado"""
    pass

class InsufficientFundsError(ApplicationError):
    """Fondos insuficientes"""
    pass

class PaymentGatewayError(ApplicationError):
    """Error en gateway de pago"""
    pass
```

---

### Manejo Explícito

```python
# ❌ MAL
def transfer_money(from_user, to_user, amount):
    try:
        from_user.balance -= amount
        to_user.balance += amount
        db.save()
    except:
        pass  # ¿Qué pasó?

# ✅ BIEN
def transfer_money(from_user, to_user, amount):
    try:
        # Validar
        if from_user.balance < amount:
            raise InsufficientFundsError(f"Insufficient funds")
        
        # Procesar
        from_user.balance -= amount
        to_user.balance += amount
        self.repo.save(from_user)
        self.repo.save(to_user)
        
    except InsufficientFundsError as e:
        logger.warning(f"Transfer failed: {e}")
        raise
    except RepositoryError as e:
        logger.error(f"Database error during transfer: {e}")
        raise ApplicationError("Unable to process transfer")
    except Exception as e:
        logger.error(f"Unexpected error during transfer: {e}")
        raise ApplicationError("An unexpected error occurred")

# En presentación
@app.post("/transfer")
def handle_transfer(request):
    try:
        result = transfer_service.transfer_money(...)
        return {"success": True}
    except InsufficientFundsError:
        return {"error": "Not enough funds"}, 400
    except ApplicationError as e:
        return {"error": str(e)}, 500
```

---

## LOGGING Y OBSERVABILIDAD

Un proyecto serio debe dejar **rastro útil**.

### Mínimo Recomendable

```python
import logging

# Configurar una sola vez
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# En cada módulo
logger = logging.getLogger(__name__)

# En servicios
class UserService:
    def register(self, user_data):
        try:
            logger.info(f"Registering user: {user_data['email']}")
            
            if self.repo.exists(user_data['email']):
                logger.warning(f"Registration failed: email exists")
                raise UserExistsError()
            
            user = self.repo.save(user_data)
            logger.info(f"User registered successfully: {user.id}")
            return user
            
        except UserExistsError:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}", exc_info=True)
            raise ApplicationError("Registration failed")
```

### Qué Loggear

✅ **Loggea:**
- Eventos importantes ("User registered", "Payment processed")
- Fallas ("User not found", "Database connection failed")
- Integraciones externas ("Payment gateway response", "Email sent")
- Tiempos relevantes (operaciones lentas)
- Identificadores técnicos útiles (user IDs, transaction IDs)

❌ **No loggees:**
- Secretos, credenciales, tokens
- Información sensible (contraseñas, números de tarjeta)
- Detalles internos innecesarios

---

## TESTING

### Diseño para Testear

```python
# ❌ DIFÍCIL DE TESTEAR
class OrderService:
    def process_order(self, order_id):
        db = connect()  # Requiere BD real
        order = db.query(f"SELECT * FROM orders...")
        response = requests.post("https://api.payment.com/charge")  # Requiere API real
        db.execute(f"UPDATE orders SET status='paid'")
        return order

# ✅ FÁCIL DE TESTEAR
class OrderService:
    def __init__(self, order_repo, payment_client):
        self.order_repo = order_repo
        self.payment_client = payment_client
    
    def process_order(self, order_id):
        order = self.order_repo.get_by_id(order_id)
        payment_result = self.payment_client.charge(order.amount)
        
        if payment_result.success:
            self.order_repo.update_status(order_id, "paid")
        
        return order

# En tests
def test_process_order():
    mock_repo = Mock()
    mock_payment = Mock()
    mock_payment.charge.return_value = Mock(success=True)
    
    service = OrderService(mock_repo, mock_payment)
    service.process_order(1)
    
    mock_repo.update_status.assert_called_once_with(1, "paid")
```

### Qué Probar

- ✅ Validaciones
- ✅ Transformaciones
- ✅ Reglas de negocio
- ✅ Casos de uso
- ✅ Adaptadores clave
- ❌ Framework plumbing
- ❌ Librerías externas (asumen que funcionan)

---

## INYECCIÓN DE DEPENDENCIAS

### Sin Dogma

No hace falta un contenedor complejo. Empieza simple:

```python
# Forma simple (suficiente para la mayoría)
class UserService:
    def __init__(self, repo: UserRepository, email: EmailService):
        self.repo = repo
        self.email = email

# Uso
service = UserService(SQLUserRepository(), GmailEmailService())

# En tests
service = UserService(MockRepository(), MockEmailService())
```

### Contenedor DI (Si Necesitas)

Solo cuando la complejidad lo justifique:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Configuración
    config = providers.Configuration()
    
    # Singletons
    db = providers.Singleton(DatabaseConnection)
    
    # Factories
    user_repo = providers.Factory(UserRepository, db=db)
    email_service = providers.Factory(EmailService)
    
    # Servicios
    user_service = providers.Factory(
        UserService,
        repo=user_repo,
        email=email_service
    )

# Uso
container = Container()
container.config.from_yaml('config.yaml')
service = container.user_service()
```

---

## NAMING Y ORGANIZACIÓN

### Recomendaciones

```python
# ✅ BIEN
- user_service.py
- payment_repository.py
- settings.py
- test_user_service.py
- UserAlreadyExistsError
- validate_email()
- MAX_EMAIL_LENGTH

# ❌ MAL
- helpers.py (con 60 funciones)
- utils.py (como cajón de sastre)
- misc.py
- final_final_v2.py
- u_svc.py
- calc_tax_amt()
- max_e_len
```

### Convención de Tests

```python
# Archivo de test refleja qué está siendo testeado
tests/
├── unit/
│   ├── test_user_service.py       # Testa UserService
│   ├── test_validators.py         # Testa validadores
│   └── test_models.py             # Testa modelos
│
└── integration/
    └── test_order_workflow.py      # Testa workflow completo
```

---

## TOOLING MÍNIMO

Un proyecto profesional debería definir:

```
✅ Formateo automático       (black, ruff)
✅ Linting                   (ruff, pylint)
✅ Tests                     (pytest)
✅ Type checking (opcional)  (mypy si aporta valor)
✅ Pre-commit hooks          (pre-commit)
✅ CI básica                 (GitHub Actions, GitLab CI)
```

### Stack Recomendado Hoy

```bash
# pyproject.toml
[tool.black]
line-length = 100

[tool.ruff]
select = ["E", "F", "W"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
```

---

## DOCUMENTACIÓN OBLIGATORIA

### README.md

Debe explicar:
- Qué hace el proyecto
- Cómo instalar
- Cómo ejecutar
- Estructura general
- Comandos básicos

### ARCHITECTURE.md

Cubre:
- Capas y responsabilidades
- Decisiones base
- Flujo de datos
- Reglas de organización

### ADRs (Architecture Decision Records)

Registran decisiones técnicas importantes:

```markdown
# ADR 0001: Use Service Layer Pattern

## Context
We need to separate business logic from data access.

## Decision
We will use a Service layer pattern.

## Consequences
- Easier to test business logic
- Clear separation of concerns
- More layers to maintain
```

---

## SEGURIDAD BÁSICA

### Mínimos desde Diseño

```python
# ❌ MAL
api_key = "sk-1234567890"  # Hardcoded
password = "admin123"       # En código
SECRET_KEY = "secret"       # Visible

# ✅ BIEN
api_key = os.getenv("API_KEY")
password = os.getenv("DB_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

# Con validación
if not os.getenv("API_KEY"):
    raise ValueError("API_KEY not configured")
```

### Checklist

- ✅ No hardcodear secretos
- ✅ No exponer tokens en logs
- ✅ Validar entradas
- ✅ No loggear información sensible
- ✅ Restringir permisos donde aplique
- ✅ Revisar dependencias vulnerables
- ✅ Manejar credenciales por entorno

---

## CUÁNDO REFACTORIZAR

No esperes a que el repo esté roto.

### Refactoriza Cuando Aparezca

- ❌ Archivos enormes (>500 líneas)
- ❌ Lógica duplicada
- ❌ Imports circulares
- ❌ Dificultad para testear
- ❌ Cambios pequeños rompen mucho
- ❌ Miedo a tocar módulos críticos
- ❌ Flujos difíciles de seguir

### Regla

**Refactorizar no es adorno. Es mantenimiento preventivo.**

---

## CHECKLISTS

### Checklist de Inicio para Nuevo Proyecto

#### Alcance
- [ ] ¿Qué resuelve el proyecto?
- [ ] ¿Qué tan probable es que crezca?
- [ ] ¿Cuánto tiempo vivirá?

#### Arquitectura
- [ ] ¿Qué capas necesito hoy?
- [ ] ¿Qué no necesito todavía?
- [ ] ¿Dónde pondré reglas de negocio?

#### Persistencia
- [ ] ¿Habrá BD?
- [ ] ¿SQL crudo, ORM o repositorios?
- [ ] ¿Cómo versionaré cambios de esquema?

#### Configuración
- [ ] ¿Dónde estarán variables de entorno?
- [ ] ¿Cómo distinguiré local, test y producción?

#### Calidad
- [ ] ¿Cómo correré tests?
- [ ] ¿Qué formatter/linter usaré?
- [ ] ¿Habrá CI?

#### Operación
- [ ] ¿Cómo registraré errores?
- [ ] ¿Cómo se hará troubleshooting?
- [ ] ¿Qué documentación mínima dejaré?

---

### Checklist de Auditoría para Proyecto Existente

- [ ] ¿Los archivos son razonablemente pequeños (<500 líneas)?
- [ ] ¿Las responsabilidades están separadas?
- [ ] ¿La UI conoce detalles de persistencia?
- [ ] ¿La lógica de negocio está centralizada?
- [ ] ¿Las constantes tienen una sola fuente de verdad?
- [ ] ¿La configuración está centralizada?
- [ ] ¿Se puede probar la lógica sin infraestructura completa?
- [ ] ¿El logging es útil?
- [ ] ¿La estructura permite agregar funcionalidades nuevas sin ensuciar?
- [ ] ¿Un tercero puede entender el flujo sin explicación verbal?

---

## REGLAS DE ORO

1. **Cada archivo debe tener una responsabilidad clara.**
   Si no puedes describirla en una línea, probablemente hace demasiado.

2. **Si una pieza mezcla UI, negocio e infraestructura, está mal cortada.**
   Las capas no deben traspasar límites.

3. **No disperses reglas de negocio ni constantes.**
   Single source of truth es obligatorio.

4. **La configuración debe centralizarse.**
   Un solo lugar para settings.

5. **Las integraciones deben aislarse detrás de adaptadores.**
   Si cambias el provider, solo cambia el adaptador.

6. **Diseña para probar.**
   Si es difícil testear, el diseño está mal.

7. **Los scripts deben reutilizar lógica, no duplicarla.**
   Extrae servicios que cualquiera pueda consumir.

8. **Un monolito ordenado vale más que una arquitectura "sofisticada" mal resuelta.**
   Prefiere orden a complejidad prematura.

9. **Refactoriza antes de que el miedo a tocar el código sea normal.**
   El mantenimiento preventivo es más barato.

10. **La arquitectura correcta es la que reduce fricción futura.**
    No la que se ve más compleja.

---

## POSICIÓN TÉCNICA FINAL

> La mayoría de proyectos no fracasan por falta de patrones avanzados.
> Fracasan por desorden básico:
> - Capas mezcladas
> - Configuración dispersa
> - Reglas duplicadas
> - Tests débiles
> - Infraestructura filtrada por todo lado

La mejor arquitectura inicial suele ser:

✅ **Simple** - No sobre-diseñes  
✅ **Modular** - Responsabilidades claras  
✅ **Explícita** - Fácil de entender  
✅ **Testeable** - Diseñada para probar  
✅ **Preparada para crecer** - Sin sobrediseño  

Ese es el criterio que conviene conservar.

---

**Esta guía es un documento vivo y debe actualizarse regularmente con nuevas lecciones aprendidas.**

**Última actualización:** Marzo 2026  
**Contribuidores:** Equipo de Arquitectura  
**Licencia:** MIT

