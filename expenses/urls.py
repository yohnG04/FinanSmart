from django.urls import path

from expenses.views import (
    ExpenseCreateView,
    ExpenseListView,
    IncomeCreateView,
    IncomeListView,
    SavingsGoalCreateView,
    SavingsGoalListView,
    SavingsContributionCreateView,
)


app_name = "expenses"

urlpatterns = [
    path(
        "",
        ExpenseListView.as_view(),
        name="expense-list",
    ),
    path(
        "gastos/nuevo/",
        ExpenseCreateView.as_view(),
        name="expense-create",
    ),
    path(
    "ingresos/",
    IncomeListView.as_view(),
    name="income-list",
    ),
    path(
        "ingresos/nuevo/",
        IncomeCreateView.as_view(),
        name="income-create",
    ),
    path(
        "metas/",
        SavingsGoalListView.as_view(),
        name="savings-goal-list",
    ),
    path(
        "metas/nueva/",
        SavingsGoalCreateView.as_view(),
        name="savings-goal-create",
    ),
    path(
        "metas/<int:goal_id>/abonar/",
        SavingsContributionCreateView.as_view(),
        name="savings-contribution-create",
    ),
]