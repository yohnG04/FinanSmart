# HTTPS en AWS

Aplicación: https://54.210.252.126

El despliegue usa `docker-compose.yml` junto con `docker-compose.tls.yml`. En el `.env` privado del servidor se configura:

```dotenv
COMPOSE_FILE=docker-compose.yml:docker-compose.tls.yml
HTTP_PORT=80
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://54.210.252.126
VOLT_BASE_URL=http://3.222.65.2
```

El override TLS solo se activa después de obtener el certificado. Nginx monta el volumen `certbot_data` en modo de solo lectura y sirve el certificado `finansmart-ip`. El volumen `acme_data` sirve las validaciones HTTP de Let's Encrypt. No eliminar estos volúmenes ni el volumen de PostgreSQL.

## Emisión inicial

Con el Compose base HTTP activo y el puerto 80 accesible:

```bash
sudo docker compose -f docker-compose.yml run --rm certbot certonly --webroot -w /var/www/certbot --preferred-profile shortlived --ip-address 54.210.252.126 --cert-name finansmart-ip --non-interactive --agree-tos --register-unsafely-without-email
```

Después se activa el override TLS y las variables anteriores, y se ejecuta `sudo docker compose up -d`. El puerto 443 debe estar permitido por el grupo de seguridad. No volver a emitir un certificado en cada despliegue.

## Renovación

El servidor tiene `finansmart-certificate.timer` activo dos veces al día, con retardo aleatorio de hasta 30 minutos. Ejecuta `/bin/sh /home/ubuntu/FinanSmart/scripts/renew-certificate.sh` como root. Ese script renueva cuando corresponde, comprueba Nginx y recarga los certificados. El certificado de IP tiene duración corta; EC2 y el laboratorio deben estar activos para renovarlo.

```bash
sudo systemctl status finansmart-certificate.timer
sudo journalctl -u finansmart-certificate.service --no-pager -n 40
sudo docker compose run --rm certbot certificates
```

Tras recrear Django o Flask, recargar Nginx para actualizar sus direcciones internas:

```bash
sudo docker compose exec -T nginx nginx -t
sudo docker compose exec -T nginx nginx -s reload
```

Las claves y tokens permanecen fuera de Git. La API para Volt debe consumirse directamente por HTTPS.

Referencia: https://letsencrypt.org/2026/03/11/shorter-certs-certbot.html
