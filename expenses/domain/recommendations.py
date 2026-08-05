from decimal import Decimal
from typing import Protocol


class RecommendationEngine(Protocol):
    def generate(
        self,
        *,
        category_name: str,
        spent: Decimal,
        limit: Decimal,
    ) -> str:
        """Genera una recomendación según el presupuesto."""


class RecommendationFactory(Protocol):
    def create(self) -> RecommendationEngine:
        """Crea el motor de recomendaciones configurado."""