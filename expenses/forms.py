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

    def clean_date(self):
        expense_date = self.cleaned_data["date"]

        if expense_date > timezone.localdate():
            raise forms.ValidationError(
                "La fecha no puede estar en el futuro."
            )

        return expense_date