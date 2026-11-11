from decimal import Decimal
import django.core.validators
import django.db.models.deletion
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='PremiumPlan', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre del plan')),
            ('description', models.TextField(blank=True, verbose_name='Descripción')),
            ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Precio (COP)')),
            ('duration_days', models.PositiveSmallIntegerField(default=30, verbose_name='Duración en días')),
            ('is_active', models.BooleanField(default=True, verbose_name='Disponible')),
        ], options={'ordering': ['price', 'pk'], 'verbose_name': 'plan premium', 'verbose_name_plural': 'planes premium'}),
        migrations.CreateModel(name='Payment', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('reference', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Importe (COP)')),
            ('status', models.CharField(choices=[('pending', 'Pendiente'), ('approved', 'Aprobado'), ('rejected', 'Rechazado')], default='pending', max_length=12, verbose_name='Estado')),
            ('simulated', models.BooleanField(default=True, verbose_name='Simulación')),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('processed_at', models.DateTimeField(blank=True, null=True)),
            ('valid_until', models.DateTimeField(blank=True, null=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='premium_payments', to=settings.AUTH_USER_MODEL)),
            ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='premium.premiumplan')),
        ], options={'ordering': ['-created_at', '-id'], 'verbose_name': 'pago', 'verbose_name_plural': 'pagos'}),
        migrations.CreateModel(name='ReportJob', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('year', models.PositiveSmallIntegerField(verbose_name='Año')),
            ('month', models.PositiveSmallIntegerField(verbose_name='Mes')),
            ('status', models.CharField(choices=[('queued', 'En cola'), ('running', 'Procesando'), ('done', 'Listo'), ('failed', 'No disponible')], default='queued', max_length=10, verbose_name='Estado')),
            ('result', models.JSONField(blank=True, default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('completed_at', models.DateTimeField(blank=True, null=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_jobs', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-created_at', '-id'], 'verbose_name': 'reporte', 'verbose_name_plural': 'reportes'}),
    ]
