from django.contrib import admin

from expenses.models import (
    Budget,
    Category,
    Expense,
    Income,
    SavingsGoal,
    SavingsContribution,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "active")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "category",
        "amount_limit",
        "month",
        "year",
    )
    list_filter = ("year", "month", "category")
    search_fields = (
        "user__username",
        "category__name",
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "category",
        "amount",
        "date",
    )
    list_filter = ("category", "date")
    search_fields = (
        "user__username",
        "description",
    )
    readonly_fields = ("created_at",)

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "category",
        "amount",
        "date",
    )
    list_filter = (
        "category",
        "date",
    )
    search_fields = (
        "user__username",
        "description",
    )
    readonly_fields = (
        "created_at",
    )


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "target_amount",
        "current_amount",
        "target_date",
    )
    search_fields = (
        "user__username",
        "name",
    )
    readonly_fields = (
        "created_at",
    )


@admin.register(SavingsContribution)
class SavingsContributionAdmin(admin.ModelAdmin):
    list_display = (
        "goal",
        "amount",
        "date",
    )
    list_filter = ("date",)
    search_fields = ("goal__name",)
    readonly_fields = ("created_at",)