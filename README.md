# FinanSmart

FinanSmart es una aplicación web de gestión financiera personal desarrollada con **Django** y **Django REST Framework**.

La aplicación permite registrar y consultar gastos, ingresos y metas de ahorro, realizar abonos a las metas, validar gastos frente a presupuestos y generar recomendaciones financieras.

El proyecto utiliza una arquitectura basada en separación de responsabilidades, **Service Layer**, **Builder**, **Factory** e inyección de dependencias.

---

## Requisitos

Para ejecutar el proyecto se necesita:

* Python 3
* pip
* Git
* Las dependencias incluidas en `requirements.txt`

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/yohnG04/FinanSmart.git
cd FinanSmart
```

### 2. Crear un entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

## Variables de entorno

El proyecto incluye un archivo `.env.example` que sirve como referencia para la configuración local.

Crear un archivo `.env` a partir de `.env.example`.

En macOS o Linux se puede utilizar:

```bash
cp .env.example .env
```

La variable:

```env
RECOMMENDATION_ENGINE=MOCK
```

permite seleccionar el motor utilizado para generar recomendaciones financieras.

Los valores disponibles son:

```env
RECOMMENDATION_ENGINE=MOCK
```

para utilizar el motor simulado, o:

```env
RECOMMENDATION_ENGINE=REAL
```

para utilizar la implementación real configurada en el proyecto.

El archivo `.env` contiene configuración local y no debe subirse al repositorio.

---

## Preparar la base de datos

Ejecutar las migraciones:

```bash
python manage.py migrate
```

Opcionalmente, crear un superusuario para acceder al panel administrativo de Django:

```bash
python manage.py createsuperuser
```

---

## Ejecutar el proyecto

```bash
python manage.py runserver
```

El servidor de desarrollo estará disponible normalmente en:

```text
http://127.0.0.1:8000/
```

---

## Funcionalidades principales

Actualmente FinanSmart permite:

* Inicio de sesión mediante autenticación de Django.
* Registro y consulta de gastos.
* Registro y consulta de ingresos.
* Creación y consulta de metas de ahorro.
* Registro y consulta de abonos a metas.
* Cálculo del progreso de las metas.
* Cálculo del monto faltante para completar una meta.
* Validación de gastos frente al presupuesto mensual.
* Cálculo del gasto acumulado.
* Generación de recomendaciones financieras.
* Uso de recomendaciones mediante modos `MOCK` y `REAL`.
* Interfaz web.
* API REST.

---

## Rutas principales del frontend

La aplicación cuenta con una interfaz web que permite utilizar las funcionalidades principales desde el navegador.

| Ruta                       | Descripción                             |
| -------------------------- | --------------------------------------- |
| `/`                        | Página principal y listado de gastos    |
| `/gastos/nuevo/`           | Registrar un nuevo gasto                |
| `/ingresos/`               | Consultar los ingresos registrados      |
| `/ingresos/nuevo/`         | Registrar un nuevo ingreso              |
| `/metas/`                  | Consultar las metas de ahorro           |
| `/metas/nueva/`            | Crear una nueva meta de ahorro          |
| `/metas/<goal_id>/abonar/` | Registrar un abono a una meta de ahorro |

Para acceder a las funcionalidades asociadas a información financiera, el usuario debe haber iniciado sesión.

---

## API REST

La API está construida utilizando **Django REST Framework**.

Entre las rutas principales se encuentran:

| Método | Endpoint                                      | Descripción                             |
| ------ | --------------------------------------------- | --------------------------------------- |
| GET    | `/api/expenses/`                              | Listar gastos del usuario autenticado   |
| POST   | `/api/expenses/`                              | Registrar un gasto                      |
| GET    | `/api/incomes/`                               | Listar ingresos del usuario autenticado |
| POST   | `/api/incomes/`                               | Registrar un ingreso                    |
| GET    | `/api/savings-goals/`                         | Listar metas de ahorro                  |
| POST   | `/api/savings-goals/`                         | Crear una meta de ahorro                |
| GET    | `/api/savings-goals/<goal_id>/contributions/` | Listar los abonos de una meta           |
| POST   | `/api/savings-goals/<goal_id>/contributions/` | Registrar un abono a una meta           |

Los endpoints relacionados con información financiera requieren que el usuario esté autenticado.

---

## Códigos HTTP utilizados

La API utiliza diferentes códigos HTTP según el resultado de la operación.

### 200 OK

Se utiliza cuando una consulta GET se procesa correctamente.

```text
GET /api/expenses/
→ 200 OK
```

### 201 Created

Se utiliza cuando un recurso es creado correctamente.

```text
POST /api/expenses/
→ 201 Created
```

También puede utilizarse en la creación de ingresos, metas de ahorro y contribuciones.

### 400 Bad Request

Se utiliza cuando los datos enviados presentan errores de validación.

```text
POST /api/incomes/
→ 400 Bad Request
```

### 404 Not Found

Se utiliza cuando el recurso solicitado no existe o no pertenece al usuario correspondiente.

```text
GET /api/savings-goals/999/contributions/
→ 404 Not Found
```

### 409 Conflict

Se utiliza cuando la solicitud es válida, pero existe un conflicto con una regla del dominio.

Por ejemplo, cuando se intenta registrar un gasto y no existe un presupuesto para la categoría y período correspondientes.

```text
POST /api/expenses/
→ 409 Conflict
```

---

## Arquitectura

El flujo general de FinanSmart sigue la estructura:

```text
View / APIView
       ↓
Form / Serializer
       ↓
Service Layer
       ↓
Dominio / Builder / Reglas
       ↓
Infraestructura / Factory
       ↓
Models / Base de datos
```

La arquitectura busca mantener separadas las responsabilidades de presentación, validación, lógica de negocio, dominio, infraestructura y persistencia.

La lógica de negocio se mantiene principalmente en el **Service Layer**, evitando colocar reglas financieras directamente en Views o Serializers.

---

## Service Layer

FinanSmart utiliza **Service Layer** para coordinar los casos de uso principales de la aplicación.

Las Views y APIViews se encargan principalmente de:

1. Recibir la solicitud.
2. Validar los datos mediante Forms o Serializers.
3. Llamar al Service correspondiente.
4. Recibir el resultado.
5. Devolver la respuesta al usuario.

Los Services concentran las operaciones relacionadas con:

* Gastos.
* Ingresos.
* Metas de ahorro.
* Abonos.
* Consultas de información financiera.

Esto permite reutilizar la misma lógica desde la interfaz web y desde la API REST.

---

## Patrones utilizados

### Builder

`ExpenseBuilder` se utiliza para construir gastos paso a paso mediante una **Fluent Interface**.

Esto permite centralizar la construcción del objeto `Expense` y evita distribuir este proceso entre diferentes Views.

### Factory

`RecommendationEngineFactory` permite seleccionar la implementación del motor de recomendaciones según la configuración:

```text
RECOMMENDATION_ENGINE=MOCK
```

o:

```text
RECOMMENDATION_ENGINE=REAL
```

Esto permite sustituir la implementación sin modificar el flujo principal de registro de gastos.

### Service Layer

Los Services coordinan los casos de uso y concentran la lógica de negocio utilizada tanto por la interfaz web como por la API REST.

---

## Inyección de dependencias

El archivo `container.py` funciona como punto de composición de dependencias.

Conceptualmente:

```text
View / APIView
      ↓
container.py
      ↓
Service
      ↓
Dependencias
```

Esto permite evitar que las Views tengan que construir directamente las implementaciones utilizadas por los Services y reduce el acoplamiento entre las capas.

---

## Seguridad

Los endpoints principales de la API utilizan autenticación.

```python
permission_classes = [IsAuthenticated]
```

Las consultas relacionadas con información financiera tienen en cuenta al usuario autenticado para evitar exponer registros pertenecientes a otras cuentas.

El flujo general es:

```text
Usuario autenticado
        ↓
APIView
        ↓
Service / Query Service
        ↓
Información del usuario
```

---

## Estructura principal del proyecto

```text
FinanSmart/
│
├── expenses/
│   ├── api/
│   ├── domain/
│   ├── infra/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── container.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
│
├── finansmart/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## Documentación

La documentación técnica completa del Entregable 1 se encuentra disponible en la **Wiki del repositorio**.

La Wiki contiene:

* Estado actual del dominio.
* Arquitectura y estructura de carpetas.
* Service Layer.
* Builder y Factory.
* Inyección de dependencias.
* Django REST Framework.
* Endpoints y códigos HTTP.
* Diagrama de secuencia.
* API Gateway y escalabilidad.
* Decisiones de diseño.
* Relación con principios SOLID.

---

## Entregable 1

Para este entregable se consideran implementadas **4 de las 7 clases principales del dominio**, correspondientes a un avance del:

**57.14 %**

### Clases principales implementadas

* Usuario (`django.contrib.auth.User`)
* Ingreso (`Income`)
* Gasto (`Expense`)
* Meta de ahorro (`SavingsGoal`)

### Entidades auxiliares

* `Category`
* `Budget`
* `SavingsContribution`

El objetivo del Entregable 1 es consolidar el núcleo de FinanSmart manteniendo entre el 50 % y el 60 % de las clases principales del dominio implementadas y respetando la arquitectura definida para el proyecto.
