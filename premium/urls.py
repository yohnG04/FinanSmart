from django.urls import path
from . import views

app_name = 'premium'
urlpatterns = [
    path('', views.plans, name='plans'),
    path('planes/<int:plan_id>/simular/', views.simulate_payment, name='simulate-payment'),
    path('reportes/', views.reports, name='reports'),
]
