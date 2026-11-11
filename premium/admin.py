from django.contrib import admin
from .models import Payment, PremiumPlan, ReportJob


@admin.register(PremiumPlan)
class PremiumPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'plan', 'amount', 'status', 'simulated', 'valid_until')
    list_filter = ('status', 'simulated')
    search_fields = ('user__username', 'reference')
    readonly_fields = ('reference', 'processed_at')


@admin.register(ReportJob)
class ReportJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('result', 'completed_at')
