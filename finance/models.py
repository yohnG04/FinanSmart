from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Debt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(_("Nombre"), max_length=150)
    principal = models.DecimalField(_("Capital inicial"), max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    balance = models.DecimalField(_("Saldo pendiente"), max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    monthly_rate = models.DecimalField(_("Interés mensual (%)"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    monthly_payment = models.DecimalField(_("Cuota mensual"), max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(balance__gte=0) & models.Q(balance__lte=models.F('principal')), name='debt_valid_balance')]

    def __str__(self):
        return self.name


class DebtContribution(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(_("Monto"), max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField(_("Fecha"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
