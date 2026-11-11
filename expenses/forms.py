from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils import timezone

from expenses.models import Category


class ExpenseForm(forms.Form):
    amount = forms.DecimalField(
        label=_('Monto'),
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _('Ejemplo: 50000'),
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label=_('Fecha'),
        widget=forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        ),
    )

    category = forms.ModelChoiceField(
        label=_('Categoría'),
        queryset=Category.objects.none(),
        empty_label=_('Selecciona una categoría'),
    )

    description = forms.CharField(
        label=_('Descripción'),
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _('Descripción opcional'),
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = (
            Category.objects.filter(active=True)
        )

        if not self.is_bound:
            self.fields["date"].initial = timezone.localdate()


class IncomeForm(forms.Form):
    amount = forms.DecimalField(
        label=_('Monto'),
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _('Ejemplo: 1200000'),
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label=_('Fecha'),
        widget=forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        ),
    )

    category = forms.ModelChoiceField(
        label=_('Categoría'),
        queryset=Category.objects.none(),
        empty_label=_('Selecciona una categoría'),
    )

    description = forms.CharField(
        label=_('Descripción'),
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _('Descripción opcional'),
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = (
            Category.objects.filter(active=True)
        )

        if not self.is_bound:
            self.fields["date"].initial = timezone.localdate()


class SavingsGoalForm(forms.Form):
    name = forms.CharField(
        label=_('Nombre de la meta'),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": _('Ejemplo: Comprar computador')
            }
        ),
    )

    target_amount = forms.DecimalField(
        label=_('Monto objetivo'),
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _('Ejemplo: 5000000'),
                "step": "0.01",
            }
        ),
    )

    current_amount = forms.DecimalField(
        label=_('Monto actual'),
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _('Ejemplo: 1000000'),
                "step": "0.01",
            }
        ),
    )

    target_date = forms.DateField(
        label=_('Fecha objetivo'),
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        ),
    )


class SavingsContributionForm(forms.Form):
    amount = forms.DecimalField(
        label=_('Monto del abono'),
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _('Ejemplo: 200000'),
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label=_('Fecha'),
        widget=forms.DateInput(
            attrs={"type": "date"}, format="%Y-%m-%d"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound:
            self.fields["date"].initial = timezone.localdate()
