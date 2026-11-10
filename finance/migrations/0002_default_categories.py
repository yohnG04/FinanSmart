from django.db import migrations


def seed(apps, schema_editor):
    category = apps.get_model('expenses', 'Category')
    for name in ['Alimentación', 'Transporte', 'Vivienda', 'Salud', 'Educación', 'Ocio', 'Salario', 'Otros']:
        category.objects.get_or_create(name=name, defaults={'active': True})


class Migration(migrations.Migration):
    dependencies = [('finance', '0001_initial'), ('expenses', '0003_savingscontribution')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
