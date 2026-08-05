from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import Sum

from expenses.domain.exceptions import BudgetNotFoundError
from expenses.domain.expense_builder import ExpenseBuilder
from expenses.domain.recommendations import RecommendationFactory
from expenses.models import Budget, Expense


@dataclass(frozen=True)
class ExpenseRegistrationResult:
    expense: Expense
    spent: Decimal
    limit: Decimal
    percentage: Decimal
    recommendation: str


class ExpenseRegistrationService:
    def __init__(
        self,
        recommendation_factory: RecommendationFactory,
    ) -> None:
        self._recommendation_factory = recommendation_factory

    @transaction.atomic
    def register(
        self,
        *,
        user: Any,
        data: dict[str, Any],
    ) -> ExpenseRegistrationResult:
        expense = self._build_expense(
            user=user,
            data=data,
        )

        budget = self._find_budget(expense)

        expense.save()

        spent = self._calculate_monthly_spending(expense)

        percentage = (
            spent / budget.amount_limit
        ) * Decimal("100")

        engine = self._recommendation_factory.create()

        recommendation = engine.generate(
            category_name=expense.category.name,
            spent=spent,
            limit=budget.amount_limit,
        )

        return ExpenseRegistrationResult(
            expense=expense,
            spent=spent,
            limit=budget.amount_limit,
            percentage=percentage,
            recommendation=recommendation,
        )

    @staticmethod
    def _build_expense(
        *,
        user: Any,
        data: dict[str, Any],
    ) -> Expense:
        return (
            ExpenseBuilder()
            .for_user(user)
            .with_amount(data["amount"])
            .in_category(data["category"])
            .on_date(data["date"])
            .with_description(data.get("description", ""))
            .build()
        )

    @staticmethod
    def _find_budget(expense: Expense) -> Budget:
        budget = (
            Budget.objects.select_for_update()
            .filter(
                user=expense.user,
                category=expense.category,
                month=expense.date.month,
                year=expense.date.year,
            )
            .first()
        )

        if budget is None:
            raise BudgetNotFoundError(
                "No tienes un presupuesto configurado para "
                f"{expense.category.name} en "
                f"{expense.date.month}/{expense.date.year}."
            )

        return budget

    @staticmethod
    def _calculate_monthly_spending(
        expense: Expense,
    ) -> Decimal:
        result = Expense.objects.filter(
            user=expense.user,
            category=expense.category,
            date__month=expense.date.month,
            date__year=expense.date.year,
        ).aggregate(
            total=Sum("amount")
        )

        return result["total"] or Decimal("0.00")