import json
import logging
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils.translation import get_language, gettext as _

from expenses.infra.recommendation_engines import BudgetRecommendationEngine

logger = logging.getLogger(__name__)


class RemoteRecommendationEngine:
    """Django calls the extracted Flask service; the local engine is a fallback."""

    def __init__(self, transport=urlopen, fallback=None):
        self.transport = transport
        self.fallback = fallback or BudgetRecommendationEngine()

    def generate(self, *, category_name: str, spent: Decimal, limit: Decimal) -> str:
        language = 'en' if get_language().startswith('en') else 'es'
        payload = json.dumps({
            'category_name': category_name,
            'spent': str(spent),
            'limit': str(limit),
            'language': language,
        }).encode('utf-8')
        request = Request(
            settings.RECOMMENDATION_SERVICE_URL,
            data=payload,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            method='POST',
        )
        try:
            with self.transport(request, timeout=3) as response:
                data = response.read(16385)
            if len(data) > 16384:
                raise ValueError('response too large')
            parsed = json.loads(data)
            recommendation = parsed['recommendation']
            if not isinstance(recommendation, str) or not recommendation.strip():
                raise ValueError('invalid recommendation')
            return recommendation
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as error:
            logger.warning('Recommendation service unavailable: %s', type(error).__name__)
            local = self.fallback.generate(category_name=category_name, spent=spent, limit=limit)
            return _('Servicio de recomendaciones temporalmente no disponible. ') + local
