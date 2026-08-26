from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import Sum

from expenses.domain.exceptions import BudgetNotFoundError
from expenses.domain.expense_builder import ExpenseBuilder
from expenses.domain.recommendations import RecommendationFactory
from expenses.models import Budget, Expense

from django.core.exceptions import ValidationError
from django.utils import timezone

from expenses.domain.exceptions import (
    BudgetNotFoundError,
    CategoryNotFoundError,
    IncomeDomainError,
    SavingsContributionDomainError,
    SavingsGoalDomainError,
    SavingsGoalNotFoundError,
)
from expenses.models import (
    Budget,
    Category,
    Expense,
    Income,
    SavingsContribution,
    SavingsGoal,
)


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


class IncomeRegistrationService:
    def register(
        self,
        *,
        user,
        data,
    ) -> Income:
        amount = data["amount"]
        income_date = data["date"]
        category = data["category"]
        description = data.get("description", "")

        if amount <= 0:
            raise IncomeDomainError(
                "El monto del ingreso debe ser mayor que cero."
            )

        if income_date > timezone.localdate():
            raise IncomeDomainError(
                "La fecha del ingreso no puede estar en el futuro."
            )

        income = Income(
            user=user,
            amount=amount,
            date=income_date,
            category=category,
            description=description,
        )

        try:
            income.full_clean()
        except ValidationError as error:
            raise IncomeDomainError(
                f"El ingreso contiene datos inválidos: {error}"
            ) from error

        income.save()

        return income


class SavingsGoalService:
    def create(
        self,
        *,
        user,
        data,
    ) -> SavingsGoal:
        goal = SavingsGoal(
            user=user,
            name=data["name"],
            target_amount=data["target_amount"],
            current_amount=data.get("current_amount", 0),
            target_date=data.get("target_date"),
        )

        try:
            goal.full_clean()
        except ValidationError as error:
            raise SavingsGoalDomainError(
                f"La meta contiene datos inválidos: {error}"
            ) from error

        goal.save()

        return goal

    def calculate_progress(
        self,
        goal: SavingsGoal,
    ):
        if goal.target_amount == 0:
            return 0

        return (
            goal.current_amount / goal.target_amount
        ) * 100

    def calculate_remaining_amount(
        self,
        goal: SavingsGoal,
    ):
        return goal.target_amount - goal.current_amount

    def get_for_user(
        self,
        *,
        user,
        goal_id: int,
    ) -> SavingsGoal:
        try:
            return SavingsGoal.objects.get(
                id=goal_id,
                user=user,
            )
        except SavingsGoal.DoesNotExist as error:
            raise SavingsGoalNotFoundError(
                "La meta de ahorro no existe."
            ) from error

    @transaction.atomic
    def add_contribution(
        self,
        *,
        goal: SavingsGoal,
        amount,
        contribution_date,
    ) -> SavingsContribution:
        if amount <= 0:
            raise SavingsContributionDomainError(
                "El abono debe ser mayor que cero."
            )

        if contribution_date > timezone.localdate():
            raise SavingsContributionDomainError(
                "La fecha del abono no puede estar en el futuro."
            )

        new_total = goal.current_amount + amount

        if new_total > goal.target_amount:
            remaining = goal.target_amount - goal.current_amount

            raise SavingsContributionDomainError(
                "El abono supera el monto pendiente de la meta. "
                f"Solo faltan ${remaining:,.2f}."
            )

        contribution = SavingsContribution(
            goal=goal,
            amount=amount,
            date=contribution_date,
        )

        try:
            contribution.full_clean()
        except ValidationError as error:
            raise SavingsContributionDomainError(
                f"El abono contiene datos inválidos: {error}"
            ) from error

        contribution.save()

        goal.current_amount = new_total
        goal.full_clean()
        goal.save(update_fields=["current_amount"])

        return contribution

class CategoryQueryService:
    def get_active(self, category_id: int) -> Category:
        try:
            return Category.objects.get(
                id=category_id,
                active=True,
            )
        except Category.DoesNotExist as error:
            raise CategoryNotFoundError(
                "La categoría solicitada no existe."
            ) from error