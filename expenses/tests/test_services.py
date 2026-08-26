from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from expenses.domain.exceptions import SavingsGoalNotFoundError
from expenses.models import Category, Expense, Income, SavingsContribution, SavingsGoal
from expenses.services import ExpenseQueryService, IncomeQueryService, SavingsGoalService


User = get_user_model()


class ExpenseQueryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user_expense",
            password="pass1234",
        )
        self.other_user = User.objects.create_user(
            username="user_expense_other",
            password="pass1234",
        )
        self.category = Category.objects.create(name="Comida")
        self.service = ExpenseQueryService()

    def test_list_for_user_returns_only_user_expenses(self):
        own_expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("50.00"),
            date=date(2026, 8, 20),
            description="Mercado",
        )
        Expense.objects.create(
            user=self.other_user,
            category=self.category,
            amount=Decimal("70.00"),
            date=date(2026, 8, 21),
            description="No debe verse",
        )

        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, own_expense.id)

    def test_list_for_user_without_records_returns_empty_queryset(self):
        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 0)


class IncomeQueryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user_income",
            password="pass1234",
        )
        self.other_user = User.objects.create_user(
            username="user_income_other",
            password="pass1234",
        )
        self.category = Category.objects.create(name="Salario")
        self.service = IncomeQueryService()

    def test_list_for_user_returns_only_user_incomes(self):
        own_income = Income.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("2500.00"),
            date=date(2026, 8, 10),
            description="Pago",
        )
        Income.objects.create(
            user=self.other_user,
            category=self.category,
            amount=Decimal("999.00"),
            date=date(2026, 8, 11),
            description="No debe verse",
        )

        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, own_income.id)

    def test_list_for_user_without_records_returns_empty_queryset(self):
        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 0)


class SavingsGoalServiceQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user_goal",
            password="pass1234",
        )
        self.other_user = User.objects.create_user(
            username="user_goal_other",
            password="pass1234",
        )
        self.service = SavingsGoalService()

    def test_list_for_user_returns_only_user_goals(self):
        own_goal = SavingsGoal.objects.create(
            user=self.user,
            name="Laptop",
            target_amount=Decimal("3000.00"),
            current_amount=Decimal("500.00"),
        )
        SavingsGoal.objects.create(
            user=self.other_user,
            name="Viaje",
            target_amount=Decimal("4000.00"),
            current_amount=Decimal("100.00"),
        )

        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, own_goal.id)

    def test_list_for_user_without_records_returns_empty_queryset(self):
        queryset = self.service.list_for_user(user=self.user)

        self.assertEqual(queryset.count(), 0)

    def test_list_contributions_for_goal_returns_only_goal_contributions(self):
        own_goal = SavingsGoal.objects.create(
            user=self.user,
            name="Laptop",
            target_amount=Decimal("3000.00"),
            current_amount=Decimal("700.00"),
        )
        other_goal = SavingsGoal.objects.create(
            user=self.other_user,
            name="Viaje",
            target_amount=Decimal("4000.00"),
            current_amount=Decimal("100.00"),
        )

        own_contribution = SavingsContribution.objects.create(
            goal=own_goal,
            amount=Decimal("200.00"),
            date=date(2026, 8, 18),
        )
        SavingsContribution.objects.create(
            goal=other_goal,
            amount=Decimal("50.00"),
            date=date(2026, 8, 19),
        )

        queryset = self.service.list_contributions_for_goal(
            goal=own_goal
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, own_contribution.id)

    def test_get_for_user_raises_when_goal_is_from_other_user(self):
        goal = SavingsGoal.objects.create(
            user=self.other_user,
            name="Viaje",
            target_amount=Decimal("4000.00"),
            current_amount=Decimal("100.00"),
        )

        with self.assertRaises(SavingsGoalNotFoundError):
            self.service.get_for_user(
                user=self.user,
                goal_id=goal.id,
            )

    def test_get_for_user_raises_when_goal_does_not_exist(self):
        with self.assertRaises(SavingsGoalNotFoundError):
            self.service.get_for_user(
                user=self.user,
                goal_id=99999,
            )
