# Entrega 2 integrada — 10 de noviembre de 2026

Se integraron los commits de `main` hasta `50e1e8d`, conservando sus autores, con la integración Volt de Yohn (`12bd716`). La configuración unificada usa `VOLT_BASE_URL`, también en Docker Compose; reemplaza las antiguas variables `ALLY_API_URL` y `ALLY_API_TOKEN`.

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

- Recibir origen real de Volt, configurar `VOLT_BASE_URL` y probar su servidor.
- Desplegar/verificar el conjunto en AWS y comprobar broker, worker, PostgreSQL, Nginx y Flask en funcionamiento real.
- Dar al aliado URL pública y token generado en la base de datos de ese despliegue. No reutilizar un token de SQLite local esperando que exista en AWS.
- Capturar evidencias, revisar correcciones del profesor y mantener EC2 encendida para sustentar.

Las pruebas locales usan SQLite y respuestas controladas para los servicios externos; no certifican un despliegue AWS ni una ejecución real del broker. Docker no estaba disponible en el entorno de esta integración, por lo que no se ejecutó Compose aquí.
