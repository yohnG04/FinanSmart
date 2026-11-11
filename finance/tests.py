from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import TestCase, override_settings
from django.utils import timezone, translation
from rest_framework.authtoken.models import Token

from expenses.models import Budget, Category, Income, Expense
from .models import Debt, DebtContribution
from .services import DebtService
from .integrations import FrankfurterAdapter, IntegrationUnavailable


class FinanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('owner')
        cls.other = get_user_model().objects.create_user('other')
        cls.category = Category.objects.first()

    def setUp(self):
        self.client.force_login(self.user)
        self.service = DebtService()
        self.debt = self.service.create(self.user, dict(name='Loan', principal=Decimal('1000'), monthly_rate=Decimal('2'), monthly_payment=Decimal('100')))

    def test_payment_updates_principal_and_interest(self):
        self.service.contribute(self.user, self.debt.pk, Decimal('100'), timezone.localdate())
        self.debt.refresh_from_db()
        self.assertEqual(self.debt.balance, Decimal('900'))
        self.assertEqual(self.service.interest(self.debt), Decimal('18'))
        self.assertEqual(DebtContribution.objects.count(), 1)

    def test_rejected_payments_leave_balance_unchanged(self):
        for amount, date in [(Decimal('0'), timezone.localdate()), (Decimal('1001'), timezone.localdate()), (Decimal('10'), timezone.localdate()+timedelta(days=1))]:
            with self.assertRaises(ValidationError):
                self.service.contribute(self.user, self.debt.pk, amount, date)
        self.debt.refresh_from_db()
        self.assertEqual(self.debt.balance, Decimal('1000'))
        self.assertFalse(DebtContribution.objects.exists())

    def test_other_user_cannot_read_or_pay_debt(self):
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/deudas/'), 'Loan')
        self.assertEqual(self.client.get(f'/deudas/{self.debt.pk}/abonar/').status_code, 404)
        self.assertEqual(self.client.post(f'/deudas/{self.debt.pk}/abonar/', {'amount': 10, 'date': timezone.localdate()}).status_code, 404)

    def test_budget_form_and_duplicate(self):
        data = dict(category=self.category.pk, amount_limit='500', month=timezone.localdate().month, year=timezone.localdate().year)
        self.assertEqual(self.client.post('/presupuestos/nuevo/', data).status_code, 302)
        self.assertEqual(self.client.post('/presupuestos/nuevo/', data).status_code, 200)
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 1)

    def test_complete_budget_expense_and_debt_form_flow(self):
        today=timezone.localdate()
        self.client.post('/presupuestos/nuevo/', dict(category=self.category.pk, amount_limit='500', month=today.month, year=today.year))
        response=self.client.post('/gastos/nuevo/', dict(category=self.category.pk, amount='25', date=today.isoformat(), description='Lunch'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.get(user=self.user).amount, Decimal('25'))
        response=self.client.post('/deudas/nueva/', dict(name='Second loan',principal='200',monthly_rate='1',monthly_payment='20'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Debt.objects.get(name='Second loan').balance, Decimal('200'))

    def test_interest_messages_and_date_widgets_in_english(self):
        from expenses.infra.recommendation_engines import BudgetRecommendationEngine
        self.client.cookies['django_language']='en'
        self.assertContains(self.client.get('/gastos/nuevo/'), 'value="'+timezone.localdate().isoformat()+'"')
        with translation.override('en'):
            text=BudgetRecommendationEngine().generate(category_name='Food',spent=Decimal('80'),limit=Decimal('100'))
            self.assertIn('80.0%', text)
            self.assertIn('Warning', text)

    def test_authenticated_summary_is_scoped_and_token_accessible(self):
        Income.objects.create(user=self.user, category=self.category, amount=200, date=timezone.localdate())
        Income.objects.create(user=self.other, category=self.category, amount=999, date=timezone.localdate())
        token = Token.objects.create(user=self.user)
        self.client.logout()
        self.assertIn(self.client.get('/api/summary/').status_code, [401,403])
        response = self.client.get('/api/summary/', HTTP_AUTHORIZATION='Token '+token.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.json()['income']), Decimal('200'))

    def test_anonymous_pages_redirect_before_data_access(self):
        self.client.logout()
        for path in ['/', '/deudas/', '/presupuestos/', '/servicios/', '/metas/999/abonar/']:
            self.assertEqual(self.client.get(path).status_code, 302)

    def test_pages_render_in_both_languages(self):
        paths=['/', '/gastos/', '/gastos/nuevo/', '/ingresos/', '/ingresos/nuevo/', '/metas/', '/metas/nueva/', '/presupuestos/', '/presupuestos/nuevo/', '/deudas/', '/deudas/nueva/', f'/deudas/{self.debt.pk}/abonar/']
        for language in ['es','en']:
            self.client.cookies['django_language']=language
            for path in paths:
                response=self.client.get(path)
                self.assertEqual(response.status_code, 200, (language,path))
            self.assertContains(self.client.get('/'), 'Financial overview' if language=='en' else 'Resumen financiero')

    def test_language_switch_persists(self):
        self.client.post('/i18n/setlang/', {'language':'en','next':'/'})
        self.assertContains(self.client.get('/'), 'Financial overview')

    def test_adapter_maps_data_and_rejects_invalid_response(self):
        cache.clear()
        result=FrankfurterAdapter(Mock(return_value={'base':'USD','quote':'COP','date':'2026-11-09','rate':4200})).rate()
        self.assertEqual(result['rate'], Decimal('4200'))
        cache.clear()
        with self.assertRaises(IntegrationUnavailable):
            FrankfurterAdapter(Mock(return_value={'rate':'NaN'})).rate()

    @patch('finance.integrations.FrankfurterAdapter.rate', side_effect=IntegrationUnavailable('Unavailable'))
    @override_settings(VOLT_BASE_URL='')
    def test_integration_outage_does_not_break_page(self, mock):
        self.assertContains(self.client.get('/servicios/'), 'Unavailable')
