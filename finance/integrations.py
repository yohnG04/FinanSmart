"""Ports and adapters: external response formats never reach the templates."""
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Protocol
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _


class IntegrationUnavailable(Exception):
    pass


def fetch_json(url, token=''):
    # URLs are server configuration, never user-supplied query parameters.
    if urlsplit(url).scheme != 'https':
        raise IntegrationUnavailable(_("El servicio debe utilizar HTTPS."))
    headers = {'Accept': 'application/json', 'User-Agent': 'FinanSmart/2'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        with urlopen(Request(url, headers=headers), timeout=4) as response:
            body = response.read(262145)
        if len(body) > 262144:
            raise ValueError('response too large')
        return json.loads(body)
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise IntegrationUnavailable(_("El servicio no está disponible. Intenta más tarde.")) from error


class RateProvider(Protocol):
    def rate(self) -> dict: ...


class FrankfurterAdapter:
    def __init__(self, fetch=fetch_json):
        self.fetch = fetch

    def rate(self):
        cached = cache.get('frankfurter-usd-cop')
        if cached:
            return cached
        raw = self.fetch('https://api.frankfurter.dev/v2/rate/USD/COP')
        try:
            value = Decimal(str(raw['rate']))
            published = date.fromisoformat(raw['date'])
            if not value.is_finite() or value <= 0 or raw['base'].upper() != 'USD' or raw['quote'].upper() != 'COP':
                raise ValueError()
        except (KeyError, TypeError, ValueError, InvalidOperation, AttributeError) as error:
            raise IntegrationUnavailable(_("El servicio devolvió datos inválidos.")) from error
        result = dict(rate=value, date=published, base='USD', quote='COP', source='Frankfurter')
        cache.set('frankfurter-usd-cop', result, 900)
        return result


class IntegrationService:
    def __init__(self, rates: RateProvider):
        self.rates = rates

    def context(self):
        try:
            return {'exchange': self.rates.rate()}
        except IntegrationUnavailable as error:
            return {'exchange_error': str(error)}
