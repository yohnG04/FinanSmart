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
- Asesor de ropa Volt: adaptador POST, conversación por sesión, precio máximo por producto y validación del contrato recibido. **Pendiente conexión real: falta la IP o dominio de Volt.**

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

## Servicio a consumir del aliado: Volt

Contrato recibido el 10 de noviembre: POST `/api/chatbot/message/`, público y sin token. Configurar `VOLT_BASE_URL` con el origen real, por ejemplo `https://volt.example`, sin añadir la ruta. Admite HTTP porque el contrato del aliado lo contempla; preferir HTTPS al desplegar. No usar el localhost de otro equipo: se refiere a la máquina donde se ejecuta la petición.

`/servicios/` permite escribir una consulta (hasta 900 caracteres para reservar espacio al límite), un precio máximo opcional en COP y continuar o reiniciar una conversación. El servicio añade el límite al mensaje en español para el filtro de Volt y envía `message` y `conversation_id`. El ID se conserva en la sesión autenticada de FinanSmart, nunca se acepta desde un campo del navegador. Se muestra la última respuesta, no un historial completo. El envío exitoso redirige para evitar repetir el POST al refrescar.

`finance/volt.py` contiene FashionProvider, VoltAdapter y FashionService. Se validan respuesta, precios finitos y stock; las tarjetas ocultan productos agotados o por encima del máximo. La respuesta textual del aliado se conserva escapada y puede mencionar productos ocultos; se informa de ello. Los enlaces llevan a `/#catalogo`, pues el contrato no ofrece enlaces individuales web. No se envía resumen financiero, token de FinanSmart ni identidad del usuario: solo consulta, límite incluido en el mensaje e identificador de conversación. Los textos del proveedor se muestran en el idioma que este devuelva.

El límite es elegido por el usuario: **no se calcula automáticamente un presupuesto de ropa**. Nuestra API de resumen sigue sin cambios. El servicio específico de presupuesto de ropa sugerido en la conversación no forma parte de esta implementación.

Se probaron request/response, sesiones, filtros, errores y formularios con respuestas controladas del contrato. **No se probó todavía contra Volt real:** falta su dirección. La pantalla muestra estado pendiente si no está configurado; no hay respuestas simuladas en producción.

En Docker Compose, pasar `VOLT_BASE_URL` a `django_web`, por ejemplo `VOLT_BASE_URL: ${VOLT_BASE_URL:-}`. Las variables antiguas ALLY_API_URL/ALLY_API_TOKEN se reemplazan por VOLT_BASE_URL; Volt no requiere autenticación. Ver también `docs/VOLT_INTEGRACION.txt`.

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
