from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext as _

from expenses.models import Budget, Category, Expense, Income, SavingsGoal
from .models import Debt, DebtContribution


class DebtService:
    def list(self, user):
        return Debt.objects.filter(user=user)

    def get(self, user, pk):
        try:
            return self.list(user).get(pk=pk)
        except Debt.DoesNotExist:
            raise Http404

    def create(self, user, data):
        debt = Debt(user=user, balance=data['principal'], **data)
        debt.full_clean()
        debt.save()
        return debt

    def interest(self, debt):
        return (debt.balance * debt.monthly_rate / 100).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    @transaction.atomic
    def contribute(self, user, pk, amount, date):
        try:
            debt = Debt.objects.select_for_update().get(user=user, pk=pk)
        except Debt.DoesNotExist:
            raise Http404
        if amount <= 0 or amount > debt.balance:
            raise ValidationError(_("El abono debe ser positivo y no superar el saldo."))
        if date > timezone.localdate() or date < timezone.localdate(debt.created_at):
            raise ValidationError(_("La fecha debe estar entre la creación de la deuda y hoy."))
        contribution = DebtContribution(debt=debt, amount=amount, date=date)
        contribution.full_clean()
        contribution.save()
        debt.balance -= amount
        debt.full_clean()
        debt.save(update_fields=['balance'])
        return contribution


class BudgetService:
    def list(self, user):
        return Budget.objects.filter(user=user).select_related('category')

    def save(self, user, data):
        budget = Budget(user=user, **data)
        budget.full_clean()
        budget.save()
        return budget

    def categories(self):
        return Category.objects.filter(active=True)


class DashboardService:
    def summary(self, user):
        today = timezone.localdate()
        period = dict(date__year=today.year, date__month=today.month)
        def total(qs, field='amount'):
            return qs.aggregate(value=Sum(field))['value'] or Decimal('0.00')
        income = total(Income.objects.filter(user=user, **period))
        expense = total(Expense.objects.filter(user=user, **period))
        return dict(month=today.month, year=today.year, currency='COP', income=income,
                    expenses=expense, balance=income-expense,
                    savings=total(SavingsGoal.objects.filter(user=user), 'current_amount'),
                    debt=total(Debt.objects.filter(user=user), 'balance'))

    def recent(self, user):
        return Expense.objects.filter(user=user).select_related('category')[:5]
