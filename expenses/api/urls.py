from django.urls import path

from expenses.api.views import (
    CategoryDetailAPIView,
    ExpenseAPIView,
    IncomeAPIView,
    SavingsGoalAPIView,
    SavingsContributionAPIView,
)


urlpatterns = [
    path(
        "expenses/",
        ExpenseAPIView.as_view(),
        name="api-expenses",
    ),
    path(
        "incomes/",
        IncomeAPIView.as_view(),
        name="api-incomes",
    ),
    path(
        "savings-goals/",
        SavingsGoalAPIView.as_view(),
        name="api-savings-goals",
    ),
    path(
        "categories/<int:category_id>/",
        CategoryDetailAPIView.as_view(),
        name="api-category-detail",
    ),
    path(
    "savings-goals/<int:goal_id>/contributions/",
    SavingsContributionAPIView.as_view(),
    name="api-savings-contribution",
    ),
]