from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="nombre",
    )
    active = models.BooleanField(
        default=True,
        verbose_name="activa",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self) -> str:
        return self.name


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
        verbose_name="usuario",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="budgets",
        verbose_name="categoría",
    )
    amount_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="límite",
    )
    month = models.PositiveSmallIntegerField(
        verbose_name="mes",
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="año",
    )

    class Meta:
        ordering = ["-year", "-month", "category__name"]
        verbose_name = "presupuesto"
        verbose_name_plural = "presupuestos"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month", "year"],
                name="unique_budget_per_user_category_month",
            )
        ]

    def clean(self) -> None:
        super().clean()

        if not 1 <= self.month <= 12:
            raise ValidationError({
                "month": "El mes debe estar entre 1 y 12."
            })

    def __str__(self) -> str:
        return (
            f"{self.user} - {self.category} "
            f"({self.month}/{self.year})"
        )


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="usuario",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="categoría",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="monto",
    )
    date = models.DateField(
        verbose_name="fecha",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="descripción",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "gasto"
        verbose_name_plural = "gastos"

    def __str__(self) -> str:
        return f"{self.category}: ${self.amount}"