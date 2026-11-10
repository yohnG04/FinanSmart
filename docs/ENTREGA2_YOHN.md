# Entrega 2: bloque de Yohn y coordinación

## Alcance

Este bloque corresponde al reparto de trabajo acordado, no a una certificación de 50 puntos de la rúbrica. La nota se evalúa sobre el sistema integrado. El porcentaje de dominio es otro cálculo: con Debt se implementan 5 de las 7 clases propuestas (71,43 %); PremiumPlan y Payment quedan a cargo del compañero.

### Implementado aquí

- Frontend Django adaptable a móvil: navegación, panel mensual, gastos, ingresos, metas, presupuestos, deudas y servicios.
- Presupuestos por usuario, categoría y periodo, con rechazo de duplicados. Categorías iniciales mediante migración; son datos editables desde administración.
- Debt y DebtContribution: alta, listado, saldo, abonos e historial. Los abonos se procesan en transacción con bloqueo de fila y no pueden superar el saldo. Ningún usuario puede acceder a las deudas de otro.
- Regla provisional explícita: tasa mensual sobre saldo para estimar interés, redondeo a dos decimales. No se capitaliza ni se cobra automáticamente. Abonos aplicados a capital, con fecha entre creación de la deuda y hoy. Confirmar contra el diseño original antes de cambiar esta regla.
- Español e inglés mediante gettext, catálogos PO/MO y selector persistente. Los nombres y descripciones ingresados por usuarios no se traducen.
- Servicio JSON autenticado: resumen mensual financiero.
- Consumo externo real de Frankfurter mediante Adapter e interfaz RateProvider, con inyección de dependencias. Timeout, validación, caché de 15 minutos y aviso si falla.
- Adaptador de equipo aliado, configuración por entorno, validación de contrato y presentación segura de datos. **Pendiente la conexión real: falta que otro equipo proporcione URL, autenticación y contrato. No cuenta como integración completada.**

### Compañero

- PremiumPlan y Payment con activación y flujo de pago; traducir sus mensajes y pantallas usando los catálogos compartidos.
- Conectar el flujo Django al microservicio de recomendaciones y gestionar indisponibilidad; Flask ya existe, pero Django todavía usa su motor local.
- Redis/Celery y tarea de fondo.
- Validar Docker, Nginx y PostgreSQL; completar despliegue AWS Academy, configuración de producción, IP y evidencias.
- Actualizar diagramas de arquitectura y documentar el despliegue integrado.

## Ejecutar

Desde la raíz del repositorio, en un entorno con las dependencias de requirements.txt:

```text
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Entrar a `/accounts/login/`. `/` ahora es el panel; el listado de gastos está en `/gastos/`. Las rutas nominales existentes se conservan. No se publican credenciales ni usuarios de demostración en las migraciones.

Para probar el flujo: crear presupuesto del mes, registrar ingreso/gasto, crear meta y abonar, registrar deuda y abonar. El panel muestra ingresos menos gastos del mes; los abonos a deuda o ahorro no se registran automáticamente como gastos para evitar duplicarlos. Confirmar esta política si el modelo original requiere un libro de movimientos unificado.

## Servicio a ofrecer al aliado

`GET /api/summary/` directamente en Django; por Nginx actual: `GET /api/v1/summary/`.

Crear una cuenta exclusiva de demostración sin información personal y generar su token:

```text
python manage.py drf_create_token USUARIO_DEMO
```

El cliente debe enviar `Authorization: Token <token>` sobre HTTPS. También funciona la sesión web. El resumen corresponde únicamente a la cuenta autenticada; no hay parámetros para consultar usuarios ajenos.

```json
{
  "month": 11,
  "year": 2026,
  "currency": "COP",
  "income": "3000000.00",
  "expenses": "1200000.00",
  "balance": "1800000.00",
  "savings": "500000.00",
  "debt": "900000.00"
}
```

Los montos son cadenas decimales. `income`, `expenses` y `balance` son del mes actual de America/Bogota; `savings` y `debt` son saldos actuales. Sin autenticación se rechaza el acceso. No enviar el token a GitHub.

## Servicio a consumir del aliado

El punto 2.3 del entregable exige consumir otro equipo. Pedirles URL HTTPS, ejemplo JSON, método de autenticación y disponibilidad para la sustentación.

Configurar `ALLY_API_URL` y, si aplica, `ALLY_API_TOKEN` (Bearer). Contrato provisional:

```json
{"items": [{"title": "Título", "description": "Información relevante del servicio"}]}
```

Adaptar `finance/integrations.py:AllyAdapter` cuando llegue el contrato real. La pantalla `/servicios/` muestra el estado pendiente cuando no hay URL; nunca inventa respuestas. Si usan otra autenticación, actualizar el adaptador. En Compose el compañero debe pasar ambas variables a Django, porque la configuración local no se copia automáticamente al contenedor.

## API de terceros y Adapter

Documentación: https://frankfurter.dev/

Endpoint: `https://api.frankfurter.dev/v2/rate/USD/COP`. No requiere clave. Solo se transmite el par de monedas, no los datos financieros del usuario. La pantalla muestra fecha publicada, fuente y tasa de referencia. `IntegrationService` recibe un `RateProvider`; `FrankfurterAdapter` transforma el formato externo al formato de la aplicación. Sustituir el proveedor no requiere cambiar las vistas.

## Verificar e integrar

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test expenses finance
```

Pruebas nuevas: propiedad de datos, pagos inválidos, saldos, presupuestos duplicados, formularios completos, token del aliado, traducciones, fechas HTML, esquemas de proveedores e indisponibilidad.

Los catálogos compilados se incluyen. Para modificar traducciones con GNU gettext:

```text
python manage.py makemessages -l en -l es
python manage.py compilemessages
```

Coordinar cambios en `finansmart/settings.py`, `finansmart/urls.py`, `templates/base.html` y `locale/`. Este bloque usa una app nueva `finance` para reducir conflictos con PremiumPlan/Payment. No se modificó el microservicio Flask ni la infraestructura.

Antes de entregar: conectar al aliado real, verificar traducción de los componentes nuevos del compañero, confirmar reglas de deuda y observaciones del profesor, ejecutar pruebas integradas y recoger evidencia en AWS. Cada estudiante debe hacer sus propios commits; no atribuir trabajo ficticio.
