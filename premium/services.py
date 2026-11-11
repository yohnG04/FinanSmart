from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import Payment, PremiumPlan, ReportJob


class PremiumService:
    def available_plans(self):
        return PremiumPlan.objects.filter(is_active=True)

    def active_payment(self, user):
        return (Payment.objects.filter(
            user=user,
            status=Payment.APPROVED,
            valid_until__gt=timezone.now(),
        ).select_related('plan').order_by('-valid_until', '-id').first())

    @transaction.atomic
    def simulate_payment(self, user, plan_id, approved):
        # Bloqueamos la cuenta para serializar extensiones simultáneas de vigencia.
        get_user_model().objects.select_for_update().get(pk=user.pk)
        try:
            plan = PremiumPlan.objects.get(pk=plan_id, is_active=True)
        except PremiumPlan.DoesNotExist as error:
            raise ValidationError(_('El plan solicitado no está disponible.')) from error
        if plan.duration_days < 1:
            raise ValidationError(_('La duración del plan debe ser positiva.'))
        now = timezone.now()
        base = max(now, self.active_payment(user).valid_until) if approved and self.active_payment(user) else now
        return Payment.objects.create(
            user=user, plan=plan, amount=plan.price,
            status=Payment.APPROVED if approved else Payment.REJECTED,
            processed_at=now,
            valid_until=base + timedelta(days=plan.duration_days) if approved else None,
            simulated=True,
        )


def queue_monthly_report(user, year, month):
    today = timezone.localdate()
    if not (2000 <= year <= today.year and 1 <= month <= 12):
        raise ValidationError(_('Selecciona un período válido.'))
    if (year, month) > (today.year, today.month):
        raise ValidationError(_('No se pueden generar reportes futuros.'))

    with transaction.atomic():
        job = ReportJob.objects.create(user=user, year=year, month=month)

        def enqueue():
            from .tasks import generate_monthly_report
            try:
                generate_monthly_report.delay(job.pk)
            except Exception:
                ReportJob.objects.filter(pk=job.pk, status=ReportJob.QUEUED).update(status=ReportJob.FAILED)

        transaction.on_commit(enqueue)
    return job
