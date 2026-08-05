from django.contrib import admin

from expenses.models import Budget, Category, Expense


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