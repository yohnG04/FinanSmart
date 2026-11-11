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


class AllyAdapter:
    """Proposed contract. Adapt only this mapping once the partner supplies its API."""
    def __init__(self, fetch=fetch_json):
        self.fetch = fetch

    def items(self):
        if not settings.ALLY_API_URL:
            raise IntegrationUnavailable(_("El servicio del equipo aliado aún no está conectado."))
        raw = self.fetch(settings.ALLY_API_URL, settings.ALLY_API_TOKEN)
        try:
            items = raw['items']
            if not isinstance(items, list):
                raise ValueError()
            result = []
            for item in items[:20]:
                title, description = item['title'], item['description']
                if not isinstance(title, str) or not isinstance(description, str):
                    raise ValueError()
                result.append(dict(title=title[:150], description=description[:1000]))
            return result
        except (KeyError, TypeError, ValueError) as error:
            raise IntegrationUnavailable(_("El servicio devolvió datos inválidos.")) from error


class IntegrationService:
    def __init__(self, rates: RateProvider, ally):
        self.rates, self.ally = rates, ally

    def context(self):
        context = {}
        for key, action in [('exchange', self.rates.rate), ('ally_items', self.ally.items)]:
            try:
                context[key] = action()
            except IntegrationUnavailable as error:
                context[key + '_error'] = str(error)
        return context
