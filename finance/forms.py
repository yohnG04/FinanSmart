from decimal import Decimal
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Debt
from .services import BudgetService


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['name', 'principal', 'monthly_rate', 'monthly_payment']
        help_texts = {'monthly_rate': _("Tasa mensual. La estimación no genera cargos automáticos.")}


class ContributionForm(forms.Form):
    amount = forms.DecimalField(label=_("Monto"), max_digits=12, decimal_places=2, min_value=Decimal('.01'))
    date = forms.DateField(label=_("Fecha"), initial=timezone.localdate, widget=forms.DateInput(attrs={'type':'date'}, format='%Y-%m-%d'))


class BudgetForm(forms.Form):
    category = forms.ModelChoiceField(label=_("Categoría"), queryset=None)
    amount_limit = forms.DecimalField(label=_("Límite mensual"), max_digits=12, decimal_places=2, min_value=Decimal('.01'))
    month = forms.IntegerField(label=_("Mes"), min_value=1, max_value=12)
    year = forms.IntegerField(label=_("Año"), min_value=2000, max_value=2100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = BudgetService().categories()
        self.fields['month'].initial = timezone.localdate().month
        self.fields['year'].initial = timezone.localdate().year
