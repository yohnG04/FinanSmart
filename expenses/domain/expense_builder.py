from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone

from expenses.domain.exceptions import ExpenseBuildError
from expenses.models import Category, Expense


class ExpenseBuilder:
    def __init__(self) -> None:
        self._user: Any = None
        self._amount: Decimal | None = None
        self._category: Category | None = None
        self._date: date | None = None
        self._description = ""

    def for_user(self, user: Any) -> "ExpenseBuilder":
        self._user = user
        return self

    def with_amount(self, amount: Decimal) -> "ExpenseBuilder":
        try:
            self._amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ExpenseBuildError(
                "El monto del gasto no es válido."
            ) from error

        return self

    def in_category(
        self,
        category: Category,
    ) -> "ExpenseBuilder":
        self._category = category
        return self

    def on_date(
        self,
        expense_date: date,
    ) -> "ExpenseBuilder":
        self._date = expense_date
        return self

    def with_description(
        self,
        description: str,
    ) -> "ExpenseBuilder":
        self._description = description.strip()
        return self

    def build(self) -> Expense:
        self._validate_required_fields()
        self._validate_business_rules()

        expense = Expense(
            user=self._user,
            amount=self._amount,
            category=self._category,
            date=self._date,
            description=self._description,
        )

        try:
            expense.full_clean()
        except ValidationError as error:
            raise ExpenseBuildError(
                f"El gasto contiene datos inválidos: {error}"
            ) from error

        return expense

    def _validate_required_fields(self) -> None:
        required_fields = {
            "usuario": self._user,
            "monto": self._amount,
            "categoría": self._category,
            "fecha": self._date,
        }

        missing_fields = [
            name
            for name, value in required_fields.items()
            if value is None
        ]

        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ExpenseBuildError(
                f"Faltan campos obligatorios: {fields}."
            )

    def _validate_business_rules(self) -> None:
        if self._amount is not None and self._amount <= 0:
            raise ExpenseBuildError(
                "El monto del gasto debe ser mayor que cero."
            )

        if (
            self._date is not None
            and self._date > timezone.localdate()
        ):
            raise ExpenseBuildError(
                "La fecha del gasto no puede estar en el futuro."
            )