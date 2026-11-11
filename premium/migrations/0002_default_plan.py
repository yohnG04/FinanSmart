from decimal import Decimal
from django.db import migrations


def create_demo_plan(apps, schema_editor):
    plan = apps.get_model('premium', 'PremiumPlan')
    plan.objects.get_or_create(
        name='Premium mensual (demo)',
        defaults={
            'description': 'Plan de demostración; no se realizan cobros reales.',
            'price': Decimal('19900.00'),
            'duration_days': 30,
            'is_active': True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [('premium', '0001_initial')]
    operations = [migrations.RunPython(create_demo_plan, migrations.RunPython.noop)]
