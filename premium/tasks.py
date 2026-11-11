from decimal import Decimal

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from expenses.models import Expense, Income
from .models import ReportJob


def calculate_report(user, year, month):
    filters = {'user': user, 'date__year': year, 'date__month': month}
    income = Income.objects.filter(**filters).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expense = Expense.objects.filter(**filters).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    return {'income': str(income), 'expenses': str(expense), 'balance': str(income - expense), 'currency': 'COP'}


@shared_task(name='premium.generate_monthly_report')
def generate_monthly_report(job_id):
    job = ReportJob.objects.select_related('user').filter(pk=job_id).first()
    if job is None or job.status == ReportJob.DONE:
        return
    ReportJob.objects.filter(pk=job_id).update(status=ReportJob.RUNNING)
    try:
        result = calculate_report(job.user, job.year, job.month)
    except Exception:
        ReportJob.objects.filter(pk=job_id).update(status=ReportJob.FAILED)
        raise
    ReportJob.objects.filter(pk=job_id).update(
        status=ReportJob.DONE,
        result=result,
        completed_at=timezone.now(),
    )
