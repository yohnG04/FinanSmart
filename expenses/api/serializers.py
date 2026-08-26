from rest_framework import serializers

from expenses.models import (
    Category,
    Expense,
    Income,
    SavingsContribution,
    SavingsGoal,
)


class ExpenseCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    date = serializers.DateField()
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(active=True),
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )


class ExpenseResponseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "date",
            "category",
            "description",
        ]


class IncomeCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    date = serializers.DateField()
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(active=True),
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )


class IncomeResponseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Income
        fields = [
            "id",
            "amount",
            "date",
            "category",
            "description",
        ]


class SavingsGoalCreateSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=150,
    )
    target_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    current_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=0,
    )
    target_date = serializers.DateField(
        required=False,
        allow_null=True,
    )


class SavingsGoalResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = [
            "id",
            "name",
            "target_amount",
            "current_amount",
            "target_date",
        ]


class SavingsContributionCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    date = serializers.DateField()


class SavingsContributionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsContribution
        fields = [
            "id",
            "amount",
            "date",
        ]