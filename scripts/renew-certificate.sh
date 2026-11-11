#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose -f docker-compose.yml -f docker-compose.tls.yml run --rm certbot renew --quiet
docker compose -f docker-compose.yml -f docker-compose.tls.yml exec -T nginx nginx -t
docker compose -f docker-compose.yml -f docker-compose.tls.yml exec -T nginx nginx -s reload
