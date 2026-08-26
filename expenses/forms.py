from django import forms
from django.utils import timezone

from expenses.models import Category


class ExpenseForm(forms.Form):
    amount = forms.DecimalField(
        label="Monto",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ejemplo: 50000",
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    category = forms.ModelChoiceField(
        label="Categoría",
        queryset=Category.objects.none(),
        empty_label="Selecciona una categoría",
    )

    description = forms.CharField(
        label="Descripción",
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Descripción opcional",
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
        label="Monto",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ejemplo: 1200000",
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    category = forms.ModelChoiceField(
        label="Categoría",
        queryset=Category.objects.none(),
        empty_label="Selecciona una categoría",
    )

    description = forms.CharField(
        label="Descripción",
        required=False,
        max_length=255,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Descripción opcional",
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
        label="Nombre de la meta",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ejemplo: Comprar computador"
            }
        ),
    )

    target_amount = forms.DecimalField(
        label="Monto objetivo",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ejemplo: 5000000",
                "step": "0.01",
            }
        ),
    )

    current_amount = forms.DecimalField(
        label="Monto actual",
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ejemplo: 1000000",
                "step": "0.01",
            }
        ),
    )

    target_date = forms.DateField(
        label="Fecha objetivo",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )


class SavingsContributionForm(forms.Form):
    amount = forms.DecimalField(
        label="Monto del abono",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Ejemplo: 200000",
                "step": "0.01",
            }
        ),
    )

    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound:
            self.fields["date"].initial = timezone.localdate()