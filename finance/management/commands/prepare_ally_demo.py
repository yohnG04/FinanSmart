"""Create an isolated, fictitious API account on the server that will serve Volt."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from rest_framework.authtoken.models import Token

from expenses.models import Category, Expense, Income, SavingsGoal
from finance.models import Debt


class Command(BaseCommand):
    help = 'Create a new fictitious account and API token for the allied team.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='volt_demo')

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        if User.objects.filter(username=username).exists():
            raise CommandError('La cuenta ya existe. No se modificó. Usa otro nombre o conserva su token actual.')
        user = User.objects.create_user(username=username, password=None)
        today = timezone.localdate()
        category, _ = Category.objects.get_or_create(name='Demostración aliado')
        Income.objects.create(user=user, category=category, date=today, amount=Decimal('3200000'), description='Dato ficticio')
        Expense.objects.create(user=user, category=category, date=today, amount=Decimal('245000'), description='Dato ficticio')
        SavingsGoal.objects.create(user=user, name='Meta ficticia', target_amount=Decimal('5000000'), current_amount=Decimal('1250000'))
        Debt.objects.create(user=user, name='Deuda ficticia', principal=Decimal('1800000'), balance=Decimal('1800000'), monthly_rate=Decimal('1.5'), monthly_payment=Decimal('180000'))
        token = Token.objects.create(user=user)
        self.stdout.write('Cuenta de prueba creada, sin contraseña de acceso web ni permisos de administrador.')
        self.stdout.write('Entrega esta cabecera por privado; no la publiques:')
        self.stdout.write('Authorization: Token ' + token.key)
