from django.urls import path

from expenses.views import ExpenseCreateView, ExpenseListView


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
]