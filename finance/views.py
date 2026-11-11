from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import DebtForm, ContributionForm, BudgetForm, FashionForm
from .services import DebtService, BudgetService, DashboardService
from .integrations import IntegrationService, FrankfurterAdapter, IntegrationUnavailable
from .volt import FashionService, VoltAdapter


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            'summary': DashboardService().summary(self.request.user),
            'recent': DashboardService().recent(self.request.user)}


class DebtListView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/debts.html'

    def get_context_data(self, **kwargs):
        service = DebtService()
        return super().get_context_data(**kwargs) | {'debts': [
            {'debt': debt, 'interest': service.interest(debt)}
            for debt in service.list(self.request.user)]}


class ValidatedFormView(LoginRequiredMixin, FormView):
    template_name = 'finance/form.html'
    title = ''

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {'title': self.title}

    def form_valid(self, form):
        try:
            self.perform(form.cleaned_data)
        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)
            return self.form_invalid(form)
        messages.success(self.request, _("Guardado correctamente."))
        return super().form_valid(form)


class DebtCreateView(ValidatedFormView):
    title = _("Registrar deuda")
    form_class = DebtForm
    success_url = reverse_lazy('finance:debts')

    def perform(self, data):
        DebtService().create(self.request.user, data)


class ContributionView(ValidatedFormView):
    title = _("Abonar a deuda")
    form_class = ContributionForm
    success_url = reverse_lazy('finance:debts')

    def get_context_data(self, **kwargs):
        debt = DebtService().get(self.request.user, self.kwargs['pk'])
        return super().get_context_data(**kwargs) | {'debt': debt, 'contributions': debt.contributions.all()[:20]}

    def perform(self, data):
        DebtService().contribute(self.request.user, self.kwargs['pk'], **data)


class BudgetListView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/budgets.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {'budgets': BudgetService().list(self.request.user)}


class BudgetCreateView(ValidatedFormView):
    title = _("Crear presupuesto")
    form_class = BudgetForm
    success_url = reverse_lazy('finance:budgets')

    def perform(self, data):
        BudgetService().save(self.request.user, data)


class IntegrationView(LoginRequiredMixin, FormView):
    template_name = 'finance/integrations.html'
    form_class = FashionForm
    success_url = reverse_lazy('finance:integrations')

    def state_key(self):
        return f'volt_chat_{self.request.user.pk}'

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'reset':
            request.session.pop(self.state_key(), None)
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        state = self.request.session.get(self.state_key(), {})
        try:
            result = FashionService(VoltAdapter()).ask(
                **form.cleaned_data, conversation_id=state.get('conversation_id'))
        except IntegrationUnavailable as error:
            form.add_error(None, str(error))
            return self.form_invalid(form)
        result['question'] = form.cleaned_data['message']
        result['max_price'] = str(form.cleaned_data['max_price']) if form.cleaned_data['max_price'] is not None else ''
        self.request.session[self.state_key()] = result
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        service = IntegrationService(FrankfurterAdapter())
        return super().get_context_data(**kwargs) | service.context() | {
            'volt_configured': bool(settings.VOLT_BASE_URL),
            'chat': self.request.session.get(self.state_key()),
        }


class SummaryAPIView(APIView):
    """Authenticated JSON service for the allied team; each account sees only its data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService().summary(request.user)
        return Response({key: str(value) if key not in ('month', 'year') else value for key, value in data.items()})
