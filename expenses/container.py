from expenses.domain.expense_builder import ExpenseBuilder
from expenses.infra.recommendation_factory import (
    RecommendationEngineFactory,
)
from expenses.services import (
    CategoryQueryService,
    ExpenseQueryService,
    ExpenseRegistrationService,
    IncomeQueryService,
    IncomeRegistrationService,
    SavingsGoalService,
)


def build_expense_registration_service() -> ExpenseRegistrationService:
    return ExpenseRegistrationService(
        recommendation_factory=RecommendationEngineFactory(),
    )


def build_income_registration_service() -> IncomeRegistrationService:
    return IncomeRegistrationService()


def build_expense_query_service() -> ExpenseQueryService:
    return ExpenseQueryService()


def build_income_query_service() -> IncomeQueryService:
    return IncomeQueryService()


def build_savings_goal_service() -> SavingsGoalService:
    return SavingsGoalService()


def build_category_query_service() -> CategoryQueryService:
    return CategoryQueryService()