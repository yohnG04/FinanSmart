from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from expenses.container import build_expense_registration_service
from expenses.domain.exceptions import ExpenseDomainError
from expenses.forms import ExpenseForm
from expenses.models import Expense


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