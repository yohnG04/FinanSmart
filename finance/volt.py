"""Adapter for Volt's POST /api/chatbot/message/ contract."""
import json
from decimal import Decimal, InvalidOperation
from typing import Protocol
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils.translation import gettext as _
from .integrations import IntegrationUnavailable


def post_json(url, payload):
    request = Request(url, data=json.dumps(payload).encode('utf-8'), method='POST',
                      headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=15) as response:
            body = response.read(262145)
        if len(body) > 262144:
            raise ValueError('response too large')
        return json.loads(body)
    except (URLError, OSError, ValueError) as error:
        raise IntegrationUnavailable(_("Volt no respondió correctamente. Intenta nuevamente.")) from error


class FashionProvider(Protocol):
    def message(self, text, conversation_id=None): ...


class VoltAdapter:
    def __init__(self, send=post_json):
        self.send = send

    def message(self, text, conversation_id=None):
        base = settings.VOLT_BASE_URL.rstrip('/')
        if not base:
            raise IntegrationUnavailable(_("El asesor Volt aún no está conectado."))
        url = urlsplit(base)
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
            raise IntegrationUnavailable(_("La dirección de Volt no es válida."))
        raw = self.send(base + '/api/chatbot/message/', {
            'message': text, 'conversation_id': conversation_id,
        })
        try:
            reply = raw['reply']
            cid = raw.get('conversation_id') or raw.get('session_id')
            products = raw['products']
            if not isinstance(reply, str) or len(reply) > 12000:
                raise ValueError()
            if not isinstance(cid, str) or not 1 <= len(cid) <= 200:
                raise ValueError()
            if not isinstance(products, list) or len(products) > 100:
                raise ValueError()
            normalized = []
            for product in products:
                pid, name = product['id'], product['name']
                price = Decimal(str(product['price']))
                stock = product['stock']
                sizes = product.get('available_sizes', [])
                if type(pid) is not int or pid <= 0 or not isinstance(name, str) or not name.strip() or len(name) > 300:
                    raise ValueError()
                if not price.is_finite() or price < 0 or price > Decimal('9999999999.99') or price != price.quantize(Decimal('.01')):
                    raise ValueError()
                if type(stock) is not int or stock < 0 or not isinstance(sizes, list) or any(not isinstance(s, str) or len(s)>40 for s in sizes):
                    raise ValueError()
                description = product.get('description', '')
                if not isinstance(description, str) or len(description) > 5000:
                    raise ValueError()
                normalized.append(dict(id=pid, name=name, price=str(price), stock=stock,
                                       description=description, sizes=', '.join(sizes[:20]),
                                       store_url=base+'/#catalogo'))
            return dict(conversation_id=cid, reply=reply, products=normalized)
        except (KeyError, TypeError, ValueError, InvalidOperation, AttributeError) as error:
            raise IntegrationUnavailable(_("Volt devolvió una respuesta con formato inválido.")) from error


class FashionService:
    def __init__(self, provider: FashionProvider):
        self.provider = provider

    def ask(self, message, max_price=None, conversation_id=None):
        text = message.strip()
        if max_price is not None:
            # Volt extracts price filters from Spanish natural language.
            text += f'. Precio máximo de {max_price:.2f} COP'
        if not text or len(text) > 1000:
            raise IntegrationUnavailable(_("La consulta completa no puede superar 1000 caracteres."))
        result = self.provider.message(text, conversation_id)
        products = result['products']
        result['products'] = [p for p in products if p['stock'] > 0 and (
            max_price is None or Decimal(p['price']) <= max_price)]
        result['filtered'] = len(result['products']) != len(products)
        return result
