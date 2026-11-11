from datetime import timedelta
from decimal import Decimal
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PremiumPlan(models.Model):
    name = models.CharField(_('Nombre del plan'), max_length=100, unique=True)
    description = models.TextField(_('Descripción'), blank=True)
    price = models.DecimalField(
        _('Precio (COP)'), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    duration_days = models.PositiveSmallIntegerField(_('Duración en días'), default=30)
    is_active = models.BooleanField(_('Disponible'), default=True)

    class Meta:
        ordering = ['price', 'pk']
        verbose_name = _('plan premium')
        verbose_name_plural = _('planes premium')

    def __str__(self):
        return self.name


class Payment(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, _('Pendiente')),
        (APPROVED, _('Aprobado')),
        (REJECTED, _('Rechazado')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_payments')
    plan = models.ForeignKey(PremiumPlan, on_delete=models.PROTECT, related_name='payments')
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(_('Importe (COP)'), max_digits=12, decimal_places=2)
    status = models.CharField(_('Estado'), max_length=12, choices=STATUS_CHOICES, default=PENDING)
    simulated = models.BooleanField(_('Simulación'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = _('pago')
        verbose_name_plural = _('pagos')

    def __str__(self):
        return f'{self.reference} ({self.status})'

    @property
    def grants_access(self):
        return self.status == self.APPROVED and self.valid_until is not None and self.valid_until > timezone.now()


class ReportJob(models.Model):
    QUEUED = 'queued'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (QUEUED, _('En cola')),
        (RUNNING, _('Procesando')),
        (DONE, _('Listo')),
        (FAILED, _('No disponible')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_jobs')
    year = models.PositiveSmallIntegerField(_('Año'))
    month = models.PositiveSmallIntegerField(_('Mes'))
    status = models.CharField(_('Estado'), max_length=10, choices=STATUS_CHOICES, default=QUEUED)
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = _('reporte')
        verbose_name_plural = _('reportes')

    def __str__(self):
        return f'Reporte {self.month}/{self.year} — {self.user_id}'
