from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from expenses.domain.recommendations import RecommendationEngine
from expenses.infra.recommendation_engines import (
    BudgetRecommendationEngine,
    MockRecommendationEngine,
)


from expenses.infra.remote_recommendations import RemoteRecommendationEngine


class RecommendationEngineFactory:
    _engines = {
        "MOCK": MockRecommendationEngine,
        "REAL": BudgetRecommendationEngine,
        "REMOTE": RemoteRecommendationEngine,
    }

    def create(self) -> RecommendationEngine:
        mode = settings.RECOMMENDATION_ENGINE.strip().upper()
        engine_class = self._engines.get(mode)

        if engine_class is None:
            valid_modes = ", ".join(self._engines.keys())
            raise ImproperlyConfigured(
                _('RECOMMENDATION_ENGINE debe ser: %(value0)s.') % {'value0': f'{valid_modes}'}
            )

        return engine_class()
