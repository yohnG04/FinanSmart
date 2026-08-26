# FinanSmart

FinanSmart es una aplicación web de gestión financiera personal desarrollada con **Django** y **Django REST Framework**.

La aplicación permite registrar y consultar gastos, ingresos y metas de ahorro, realizar abonos a las metas, validar gastos frente a presupuestos y generar recomendaciones financieras.

El proyecto utiliza una arquitectura basada en separación de responsabilidades, **Service Layer**, **Builder**, **Factory** e inyección de dependencias.

## Requisitos

Para ejecutar el proyecto se necesita:

* Python 3
* pip
* Git
* Las dependencias incluidas en `requirements.txt`

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

## Variables de entorno

El proyecto incluye un archivo `.env.example` que sirve como referencia para la configuración local.

Crear un archivo `.env` a partir de `.env.example`.

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

## Preparar la base de datos

Ejecutar las migraciones:

```bash
python manage.py migrate
```

Opcionalmente, crear un superusuario para acceder al panel administrativo de Django:

```bash
python manage.py createsuperuser
```

## Ejecutar el proyecto

```bash
python manage.py runserver
```

El servidor de desarrollo estará disponible normalmente en:

```text
http://127.0.0.1:8000/
```

## Funcionalidades principales

Actualmente FinanSmart permite:

* Inicio de sesión mediante autenticación de Django.
* Registro y consulta de gastos.
* Registro y consulta de ingresos.
* Creación y consulta de metas de ahorro.
* Registro y consulta de abonos a metas.
* Cálculo del progreso de las metas.
* Validación de gastos frente al presupuesto mensual.
* Generación de recomendaciones financieras.
* Uso de recomendaciones mediante modos `MOCK` y `REAL`.
* Interfaz web.
* API REST.

## API REST

La API está construida utilizando **Django REST Framework**.

Entre las rutas principales se encuentran:

| Método | Endpoint                                      | Descripción                 |
| ------ | --------------------------------------------- | --------------------------- |
| GET    | `/api/expenses/`                              | Listar gastos del usuario   |
| POST   | `/api/expenses/`                              | Registrar un gasto          |
| GET    | `/api/incomes/`                               | Listar ingresos del usuario |
| POST   | `/api/incomes/`                               | Registrar un ingreso        |
| GET    | `/api/savings-goals/`                         | Listar metas de ahorro      |
| POST   | `/api/savings-goals/`                         | Crear una meta de ahorro    |
| GET    | `/api/savings-goals/<goal_id>/contributions/` | Listar abonos de una meta   |
| POST   | `/api/savings-goals/<goal_id>/contributions/` | Registrar un abono          |

Los endpoints relacionados con información financiera requieren que el usuario esté autenticado.

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

La lógica de negocio se mantiene principalmente en el **Service Layer**, evitando colocar reglas financieras directamente en Views o Serializers.

## Patrones utilizados

### Builder

`ExpenseBuilder` se utiliza para construir gastos paso a paso mediante una Fluent Interface.

### Factory

`RecommendationEngineFactory` permite seleccionar la implementación del motor de recomendaciones según la configuración `MOCK` o `REAL`.

### Service Layer

Los Services coordinan los casos de uso y concentran la lógica de negocio utilizada tanto por la interfaz web como por la API REST.

## Documentación

La documentación técnica completa del Entregable 1 se encuentra disponible en la **Wiki del repositorio**, donde se describe:

* Arquitectura y estructura de carpetas.
* Service Layer.
* Builder y Factory.
* Django REST Framework.
* Códigos HTTP.
* Diagrama de secuencia.
* API Gateway y escalabilidad.
* Decisiones de diseño y principios SOLID.

## Entregable 1

Para este entregable se consideran implementadas **4 de las 7 clases principales del dominio**, correspondientes a un avance del **57.14 %**:

* Usuario (`django.contrib.auth.User`)
* Ingreso (`Income`)
* Gasto (`Expense`)
* Meta de ahorro (`SavingsGoal`)

Como entidades auxiliares se encuentran:

* `Category`
* `Budget`
* `SavingsContribution`
