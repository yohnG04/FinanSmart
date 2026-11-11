# Entrega 2 integrada — actualización del 11 de noviembre de 2026

## Despliegue comprobado

- Aplicación: https://54.210.252.126 (HTTP redirige a HTTPS).
- AWS EC2 con seis servicios de Compose en ejecución; PostgreSQL, Redis y Flask saludables.
- Inicio de sesión, panel ES/EN, ingreso, gasto y registro de deuda comprobados mediante la interfaz.
- API `/api/v1/summary/` comprobada con una cuenta ficticia sin permisos administrativos. El token se entrega por privado y nunca se publica en el repositorio.
- Consulta real Frankfurter USD/COP y ruteo de recomendaciones a Flask comprobados desde AWS.
- Reporte real procesado por Celery/Redis y pagos simulados aprobado/rechazado comprobados. La prueba de pagos se revirtió sin modificar los movimientos del usuario.
- Certificado de IP emitido por Let's Encrypt, cookies seguras y temporizador de renovación `finansmart-certificate.timer` activo.
- Volt configurado con `VOLT_BASE_URL=http://3.222.65.2`. Su health responde 200, pero el chatbot devolvió 503 `llm_unavailable`. FinanSmart muestra el error sin bloquear la página. Falta la consulta exitosa cuando Volt repare su servicio.

La evidencia PDF entregada previamente refleja el estado anterior a HTTPS y a estas comprobaciones adicionales. No se reclama el bono de más del 70 % de lógica migrada.

Se integraron los commits de `main` hasta `c4f581d`, conservando sus autores, con la integración Volt de Yohn (`12bd716`). La configuración unificada usa `VOLT_BASE_URL`, también en Docker Compose; reemplaza las antiguas variables `ALLY_API_URL` y `ALLY_API_TOKEN`.

## Incluido en el código

- Frontend, panel, presupuestos, deudas e idiomas.
- Planes premium y pagos simulados del compañero (sin cobros reales).
- Reportes con Celery/Redis y motor remoto Flask con respaldo local.
- Docker Compose, Nginx y configuración de despliegue.
- Asesor Volt conforme al contrato recibido y tipo de cambio Frankfurter.
- API de resumen para el equipo aliado y comando `prepare_ally_demo` para crear una cuenta ficticia con token sin permisos administrativos.
- Configuración de pruebas automáticas de GitHub.

Las guías anteriores describen bloques individuales y asignaciones históricas. Para entregar información al equipo Volt, usar [API_PARA_EQUIPO_VOLT.txt](API_PARA_EQUIPO_VOLT.txt). Para consumir su chatbot, usar [VOLT_INTEGRACION.txt](VOLT_INTEGRACION.txt).

## Pendiente operativo

- Volt debe reparar su chatbot; después se debe comprobar una respuesta real en `/servicios/`.
- El aliado debe incorporar nuestra URL HTTPS y el token privado en su backend y aportar evidencia de su consumo.
- Mantener EC2 y el laboratorio activos para la sustentación y para las renovaciones del certificado.

Las pruebas locales usan SQLite y respuestas controladas para servicios externos. Las comprobaciones reales de AWS se enumeran arriba y complementan esas pruebas.

## Validación local

47 pruebas Django y 8 pruebas Flask aprobadas. Comprobaciones de configuración, migraciones y recolección de archivos estáticos completadas.

