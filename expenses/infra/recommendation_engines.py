from django.utils.translation import gettext as _
from decimal import Decimal


class MockRecommendationEngine:
    def generate(
        self,
        *,
        category_name: str,
        spent: Decimal,
        limit: Decimal,
    ) -> str:
        return (
            _('[MODO MOCK] Recomendación simulada: revisa tus gastos antes de realizar otra compra.')
        )


class BudgetRecommendationEngine:
    def generate(
        self,
        *,
        category_name: str,
        spent: Decimal,
        limit: Decimal,
    ) -> str:
        percentage = (spent / limit) * Decimal("100")

        if percentage < Decimal("70"):
            return (
                _('Vas bien. Has utilizado el %(value0)s%% de tu presupuesto de %(value1)s.') % {'value0': f'{percentage:.1f}', 'value1': f'{category_name}'}
            )

        if percentage < Decimal("100"):
            return (
                _('Atención: has utilizado el %(value0)s%% de tu presupuesto de %(value1)s. Reduce los gastos no esenciales.') % {'value0': f'{percentage:.1f}', 'value1': f'{category_name}'}
            )

        exceeded_amount = spent - limit

        return (
            _('Superaste tu presupuesto de %(value0)s en $%(value1)s. Revisa tus últimos gastos y ajusta tus próximas compras.') % {'value0': f'{category_name}', 'value1': f'{exceeded_amount:,.2f}'}
        )
