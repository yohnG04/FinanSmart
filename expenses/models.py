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

class Income(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="incomes",
        verbose_name="usuario",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="incomes",
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
        verbose_name = "ingreso"
        verbose_name_plural = "ingresos"

    def __str__(self) -> str:
        return f"{self.category}: ${self.amount}"


class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="savings_goals",
        verbose_name="usuario",
    )
    name = models.CharField(
        max_length=150,
        verbose_name="nombre",
    )
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="monto objetivo",
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="monto actual",
    )
    target_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha objetivo",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "meta de ahorro"
        verbose_name_plural = "metas de ahorro"

    def clean(self) -> None:
        super().clean()

        if self.current_amount > self.target_amount:
            raise ValidationError({
                "current_amount":
                    "El monto actual no puede superar el monto objetivo."
            })

    def __str__(self) -> str:
        return self.name

class SavingsContribution(models.Model):
    goal = models.ForeignKey(
        SavingsGoal,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="meta de ahorro",
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "abono de ahorro"
        verbose_name_plural = "abonos de ahorro"

    def __str__(self) -> str:
        return f"{self.goal.name}: ${self.amount}"