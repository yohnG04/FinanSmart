from expenses.infra.recommendation_factory import (
    RecommendationEngineFactory,
)
from expenses.services import ExpenseRegistrationService


def build_expense_registration_service() -> ExpenseRegistrationService:
    recommendation_factory = RecommendationEngineFactory()

    return ExpenseRegistrationService(
        recommendation_factory=recommendation_factory,
    )