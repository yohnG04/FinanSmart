from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.shortcuts import get_object_or_404
from django.http import Http404

from expenses.container import (
    build_expense_registration_service,
    build_income_registration_service,
    build_savings_goal_service,
)

from expenses.domain.exceptions import (
    ExpenseDomainError,
    IncomeDomainError,
    SavingsContributionDomainError,
    SavingsGoalDomainError,
    SavingsGoalNotFoundError,
)

from expenses.forms import (
    ExpenseForm,
    IncomeForm,
    SavingsContributionForm,
    SavingsGoalForm,
)
from expenses.models import Expense, Income, SavingsGoal
from expenses.services import (
    IncomeRegistrationService,
    SavingsGoalService,
)


class ExpenseCreateView(LoginRequiredMixin, FormView):
    template_name = "expenses/expense_form.html"
    form_class = ExpenseForm
    success_url = reverse_lazy("expenses:expense-list")
    service_provider = staticmethod(build_expense_registration_service)

    def form_valid(self, form):
        try:
            result = self.service_provider().register(
                user=self.request.user,
                data=form.cleaned_data,
            )
        except ExpenseDomainError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Gasto registrado. {result.recommendation}",
        )

        return super().form_valid(form)


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return (
            Expense.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-date", "-created_at")
        )

class IncomeCreateView(LoginRequiredMixin, FormView):
    template_name = "expenses/income_form.html"
    form_class = IncomeForm
    success_url = reverse_lazy("expenses:income-list")

    service_provider = staticmethod(
        build_income_registration_service
    )

    def form_valid(self, form):
        try:
            self.service_provider().register(
                user=self.request.user,
                data=form.cleaned_data,
            )
        except IncomeDomainError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)

        messages.success(
            self.request,
            "Ingreso registrado correctamente.",
        )

        return super().form_valid(form)


class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = "expenses/income_list.html"
    context_object_name = "incomes"

    def get_queryset(self):
        return (
            Income.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-date", "-created_at")
        )


class SavingsGoalCreateView(LoginRequiredMixin, FormView):
    template_name = "expenses/savings_goal_form.html"
    form_class = SavingsGoalForm
    success_url = reverse_lazy("expenses:savings-goal-list")

    service_provider = staticmethod(
        build_savings_goal_service
    )

    def form_valid(self, form):
        try:
            self.service_provider().create(
                user=self.request.user,
                data=form.cleaned_data,
            )
        except SavingsGoalDomainError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)

        messages.success(
            self.request,
            "Meta de ahorro creada correctamente.",
        )

        return super().form_valid(form)


class SavingsGoalListView(LoginRequiredMixin, ListView):
    model = SavingsGoal
    template_name = "expenses/savings_goal_list.html"
    context_object_name = "goals"

    service_provider = staticmethod(
        build_savings_goal_service
    )

    def get_queryset(self):
        return (
            SavingsGoal.objects.filter(user=self.request.user)
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service = self.service_provider()

        context["goals_with_progress"] = [
            {
                "goal": goal,
                "progress": round(
                    service.calculate_progress(goal),
                    2,
                ),
                "remaining": service.calculate_remaining_amount(goal),
            }
            for goal in context["goals"]
        ]

        return context


class SavingsContributionCreateView(LoginRequiredMixin, FormView):
    template_name = "expenses/savings_contribution_form.html"
    form_class = SavingsContributionForm
    success_url = reverse_lazy("expenses:savings-goal-list")

    service_provider = staticmethod(
        build_savings_goal_service
    )

    def dispatch(self, request, *args, **kwargs):
        try:
            self.goal = self.service_provider().get_for_user(
                user=request.user,
                goal_id=kwargs["goal_id"],
            )
        except SavingsGoalNotFoundError as error:
            raise Http404(str(error)) from error

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            self.service_provider().add_contribution(
                goal=self.goal,
                amount=form.cleaned_data["amount"],
                contribution_date=form.cleaned_data["date"],
            )
        except SavingsContributionDomainError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)

        messages.success(
            self.request,
            "Abono registrado correctamente.",
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.service_provider()

        context["goal"] = self.goal
        context["remaining"] = service.calculate_remaining_amount(
            self.goal
        )

        return context