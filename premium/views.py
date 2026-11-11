from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST

from .models import PremiumPlan, ReportJob
from .services import PremiumService, queue_monthly_report


@login_required
@require_http_methods(['GET'])
def plans(request):
    service = PremiumService()
    return render(request, 'premium/plans.html', {
        'plans': service.available_plans(),
        'active_payment': service.active_payment(request.user),
        'payments': request.user.premium_payments.select_related('plan')[:10],
    })


@login_required
@require_POST
def simulate_payment(request, plan_id):
    service = PremiumService()
    choice = request.POST.get('simulation')
    if choice not in ('approved', 'rejected'):
        messages.error(request, _('Selecciona una simulación válida.'))
        return redirect('premium:plans')
    try:
        payment = service.simulate_payment(request.user, plan_id, choice == 'approved')
    except ValidationError as error:
        messages.error(request, '; '.join(error.messages))
    else:
        if payment.status == payment.APPROVED:
            messages.success(request, _('Pago de prueba aprobado. Plan activado.'))
        else:
            messages.warning(request, _('Pago de prueba rechazado. No se activó el plan.'))
    return redirect('premium:plans')


@login_required
@require_http_methods(['GET', 'POST'])
def reports(request):
    today = timezone.localdate()
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year', ''))
            month = int(request.POST.get('month', ''))
            queue_monthly_report(request.user, year, month)
        except (ValueError, TypeError):
            messages.error(request, _('Selecciona un período válido.'))
        except ValidationError as error:
            messages.error(request, '; '.join(error.messages))
        else:
            messages.success(request, _('Solicitud de reporte registrada. Revisa el estado de la tarea.'))
        return redirect('premium:reports')

    return render(request, 'premium/reports.html', {
        'reports': ReportJob.objects.filter(user=request.user)[:20],
        'current_year': today.year, 'current_month': today.month,
    })
