from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone, translation
from django.urls import reverse

from expenses.models import Category, Expense, Income
from expenses.infra.remote_recommendations import RemoteRecommendationEngine
from .models import Payment, PremiumPlan, ReportJob
from .services import PremiumService
from .tasks import generate_monthly_report


class PremiumTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user('samuel-test', password='testpass_4567')
        cls.other = User.objects.create_user('other-test', password='testpass_4567')
        cls.plan = PremiumPlan.objects.create(name='Plan de prueba', price=Decimal('20000'), duration_days=30)
        cls.category, _ = Category.objects.get_or_create(name='Pruebas Premium')

    def test_purchase_requires_authentication(self):
        url = reverse('premium:simulate-payment', args=[self.plan.pk])
        self.assertEqual(self.client.post(url, {'simulation': 'approved'}).status_code, 302)
        self.assertEqual(Payment.objects.count(), 0)

    def test_success_and_rejection_differ(self):
        service = PremiumService()
        rejected = service.simulate_payment(self.owner, self.plan.pk, False)
        self.assertEqual(rejected.status, Payment.REJECTED)
        self.assertIsNone(service.active_payment(self.owner))
        approved = service.simulate_payment(self.owner, self.plan.pk, True)
        self.assertTrue(approved.grants_access)
        self.assertEqual(service.active_payment(self.owner).pk, approved.pk)
        self.assertEqual(approved.amount, self.plan.price)

    def test_subscription_extends_on_second_payment(self):
        service = PremiumService()
        first = service.simulate_payment(self.owner, self.plan.pk, True)
        second = service.simulate_payment(self.owner, self.plan.pk, True)
        self.assertEqual(second.valid_until, first.valid_until + timedelta(days=30))

    def test_rejected_or_other_user_does_not_activate(self):
        PremiumService().simulate_payment(self.other, self.plan.pk, True)
        self.assertIsNone(PremiumService().active_payment(self.owner))
        self.client.force_login(self.owner)
        response = self.client.get(reverse('premium:plans'))
        self.assertNotContains(response, 'Tu plan está activo')

    def test_create_payment_via_browser(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('premium:simulate-payment', args=[self.plan.pk]), {'simulation': 'approved'})
        self.assertRedirects(response, reverse('premium:plans'))
        self.assertEqual(Payment.objects.filter(user=self.owner, status=Payment.APPROVED).count(), 1)

    def test_report_scoped_to_owner_and_calculated(self):
        today = timezone.localdate()
        Income.objects.create(user=self.owner, category=self.category, amount=Decimal('120.00'), date=today)
        Expense.objects.create(user=self.owner, category=self.category, amount=Decimal('20.00'), date=today)
        Income.objects.create(user=self.other, category=self.category, amount=Decimal('999.00'), date=today)
        job = ReportJob.objects.create(user=self.owner, month=today.month, year=today.year)
        generate_monthly_report(job.pk)
        job.refresh_from_db()
        self.assertEqual(job.status, ReportJob.DONE)
        self.assertEqual(Decimal(job.result['balance']), Decimal('100.00'))
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(reverse('premium:reports')), '100.00')

    def test_remote_recommendation_and_fallback(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n): return b'{"recommendation":"API Flask OK"}'
        transport = lambda request, timeout: Reply()
        with override_settings(RECOMMENDATION_SERVICE_URL='http://recommendation_service:5000/api/v2/recommendations/'):
            engine = RemoteRecommendationEngine(transport=transport)
            self.assertEqual(engine.generate(category_name='Food', spent=Decimal('10'), limit=Decimal('100')), 'API Flask OK')
            def unavailable(*args, **kwargs): raise TimeoutError
            with translation.override('en'):
                fallback = RemoteRecommendationEngine(transport=unavailable).generate(category_name='Food', spent=Decimal('90'), limit=Decimal('100'))
                self.assertIn('temporarily unavailable', fallback)
