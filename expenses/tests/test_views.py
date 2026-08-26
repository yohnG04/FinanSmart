from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from expenses.models import Category, Expense, Income, SavingsContribution, SavingsGoal


User = get_user_model()


class ApiGetViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="api_user",
            password="pass1234",
        )
        self.other_user = User.objects.create_user(
            username="api_other_user",
            password="pass1234",
        )
        self.empty_user = User.objects.create_user(
            username="api_empty_user",
            password="pass1234",
        )

        self.category = Category.objects.create(name="General")

    def test_get_expenses_returns_only_authenticated_user_data(self):
        own_expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("40.00"),
            date=date(2026, 8, 15),
            description="Taxi",
        )
        Expense.objects.create(
            user=self.other_user,
            category=self.category,
            amount=Decimal("80.00"),
            date=date(2026, 8, 16),
            description="No visible",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api-expenses"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_expense.id)

    def test_get_expenses_without_records_returns_empty_list(self):
        self.client.force_authenticate(user=self.empty_user)
        response = self.client.get(reverse("api-expenses"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_incomes_returns_only_authenticated_user_data(self):
        own_income = Income.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("3000.00"),
            date=date(2026, 8, 5),
            description="Nómina",
        )
        Income.objects.create(
            user=self.other_user,
            category=self.category,
            amount=Decimal("123.00"),
            date=date(2026, 8, 6),
            description="No visible",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api-incomes"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_income.id)

    def test_get_incomes_without_records_returns_empty_list(self):
        self.client.force_authenticate(user=self.empty_user)
        response = self.client.get(reverse("api-incomes"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_savings_goals_returns_only_authenticated_user_data(self):
        own_goal = SavingsGoal.objects.create(
            user=self.user,
            name="Laptop",
            target_amount=Decimal("2000.00"),
            current_amount=Decimal("500.00"),
        )
        SavingsGoal.objects.create(
            user=self.other_user,
            name="Viaje",
            target_amount=Decimal("4000.00"),
            current_amount=Decimal("100.00"),
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api-savings-goals"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_goal.id)
        self.assertIn("progress", response.data[0])
        self.assertIn("remaining", response.data[0])

    def test_get_savings_goals_without_records_returns_empty_list(self):
        self.client.force_authenticate(user=self.empty_user)
        response = self.client.get(reverse("api-savings-goals"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_savings_contributions_success(self):
        own_goal = SavingsGoal.objects.create(
            user=self.user,
            name="Laptop",
            target_amount=Decimal("2000.00"),
            current_amount=Decimal("600.00"),
        )
        own_contribution = SavingsContribution.objects.create(
            goal=own_goal,
            amount=Decimal("100.00"),
            date=date(2026, 8, 22),
        )
        other_goal = SavingsGoal.objects.create(
            user=self.other_user,
            name="Moto",
            target_amount=Decimal("5000.00"),
            current_amount=Decimal("100.00"),
        )
        SavingsContribution.objects.create(
            goal=other_goal,
            amount=Decimal("50.00"),
            date=date(2026, 8, 23),
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse(
                "api-savings-contribution",
                kwargs={"goal_id": own_goal.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_contribution.id)

    def test_get_savings_contributions_user_cannot_access_other_user_goal(self):
        other_goal = SavingsGoal.objects.create(
            user=self.other_user,
            name="Moto",
            target_amount=Decimal("5000.00"),
            current_amount=Decimal("100.00"),
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse(
                "api-savings-contribution",
                kwargs={"goal_id": other_goal.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_savings_contributions_with_nonexistent_goal_returns_404(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse(
                "api-savings-contribution",
                kwargs={"goal_id": 99999},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
