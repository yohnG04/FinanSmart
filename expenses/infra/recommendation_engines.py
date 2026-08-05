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
            "[MODO MOCK] Recomendación simulada: "
            "revisa tus gastos antes de realizar otra compra."
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
                f"Vas bien. Has utilizado el {percentage:.1f}% "
                f"de tu presupuesto de {category_name}."
            )

        if percentage < Decimal("100"):
            return (
                f"Atención: has utilizado el {percentage:.1f}% "
                f"de tu presupuesto de {category_name}. "
                "Reduce los gastos no esenciales."
            )

        exceeded_amount = spent - limit

        return (
            f"Superaste tu presupuesto de {category_name} "
            f"en ${exceeded_amount:,.2f}. "
            "Revisa tus últimos gastos y ajusta tus próximas compras."
        )