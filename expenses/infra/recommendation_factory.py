from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from expenses.domain.recommendations import RecommendationEngine
from expenses.infra.recommendation_engines import (
    BudgetRecommendationEngine,
    MockRecommendationEngine,
)


class RecommendationEngineFactory:
    _engines = {
        "MOCK": MockRecommendationEngine,
        "REAL": BudgetRecommendationEngine,
    }

    def create(self) -> RecommendationEngine:
        mode = settings.RECOMMENDATION_ENGINE.strip().upper()
        engine_class = self._engines.get(mode)

        if engine_class is None:
            valid_modes = ", ".join(self._engines.keys())
            raise ImproperlyConfigured(
                f"RECOMMENDATION_ENGINE debe ser: {valid_modes}."
            )

        return engine_class()