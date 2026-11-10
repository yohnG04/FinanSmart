from django.urls import path
from . import views

app_name = 'finance'
urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('deudas/', views.DebtListView.as_view(), name='debts'),
    path('deudas/nueva/', views.DebtCreateView.as_view(), name='debt-create'),
    path('deudas/<int:pk>/abonar/', views.ContributionView.as_view(), name='debt-contribute'),
    path('presupuestos/', views.BudgetListView.as_view(), name='budgets'),
    path('presupuestos/nuevo/', views.BudgetCreateView.as_view(), name='budget-create'),
    path('servicios/', views.IntegrationView.as_view(), name='integrations'),
]
