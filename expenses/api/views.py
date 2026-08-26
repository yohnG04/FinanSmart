from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from expenses.api.serializers import (
    ExpenseCreateSerializer,
    ExpenseResponseSerializer,
    IncomeCreateSerializer,
    IncomeResponseSerializer,
    SavingsContributionCreateSerializer,
    SavingsContributionResponseSerializer,
    SavingsGoalCreateSerializer,
    SavingsGoalResponseSerializer,
)
from expenses.container import build_expense_registration_service
from expenses.domain.exceptions import (
    BudgetNotFoundError,
    ExpenseDomainError,
    IncomeDomainError,
    SavingsGoalDomainError,
    SavingsContributionDomainError,
    CategoryNotFoundError,
    SavingsGoalNotFoundError,
)
from expenses.container import (
    build_category_query_service,
    build_expense_query_service,
    build_expense_registration_service,
    build_income_query_service,
    build_income_registration_service,
    build_savings_goal_service,
)
from expenses.services import (
    IncomeRegistrationService,
    SavingsGoalService,
)


class ExpenseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    query_service_provider = staticmethod(
        build_expense_query_service
    )

    def get(self, request):
        expenses = self.query_service_provider().list_for_user(
            user=request.user
        )

        return Response(
            ExpenseResponseSerializer(expenses, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ExpenseCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = build_expense_registration_service().register(
                user=request.user,
                data=serializer.validated_data,
            )

        except BudgetNotFoundError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_409_CONFLICT,
            )

        except ExpenseDomainError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = ExpenseResponseSerializer(
            result.expense
        ).data

        response_data["percentage"] = str(
            round(result.percentage, 2)
        )
        response_data["recommendation"] = (
            result.recommendation
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class IncomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    service_provider = staticmethod(
                build_income_registration_service
    )
    query_service_provider = staticmethod(
        build_income_query_service
    )

    def get(self, request):
        incomes = self.query_service_provider().list_for_user(
            user=request.user
        )

        return Response(
            IncomeResponseSerializer(incomes, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = IncomeCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            income = self.service_provider().register(
                user=request.user,
                data=serializer.validated_data,
            )

        except IncomeDomainError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            IncomeResponseSerializer(income).data,
            status=status.HTTP_201_CREATED,
        )


class SavingsGoalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    service_provider = staticmethod(
      build_savings_goal_service
    )

    def get(self, request):
        service = self.service_provider()
        goals = service.list_for_user(user=request.user)

        response_data = SavingsGoalResponseSerializer(
            goals,
            many=True,
        ).data

        for goal_data, goal in zip(response_data, goals):
            goal_data["progress"] = str(
                round(service.calculate_progress(goal), 2)
            )
            goal_data["remaining"] = str(
                service.calculate_remaining_amount(goal)
            )

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = SavingsGoalCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            goal = self.service_provider().create(
                user=request.user,
                data=serializer.validated_data,
            )

        except SavingsGoalDomainError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = SavingsGoalResponseSerializer(
            goal
        ).data

        service = self.service_provider()

        response_data["progress"] = str(
            round(
                service.calculate_progress(goal),
                2,
            )
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


class CategoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    service_provider = staticmethod(
        build_category_query_service
    )

    def get(self, request, category_id):
        try:
            category = self.service_provider().get_active(
                category_id
            )
        except CategoryNotFoundError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": category.id,
                "name": category.name,
                "active": category.active,
            },
            status=status.HTTP_200_OK,
        )


class SavingsContributionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    service_provider = staticmethod(
      build_savings_goal_service
    )

    def get(self, request, goal_id):
        service = self.service_provider()

        try:
            goal = service.get_for_user(
                user=request.user,
                goal_id=goal_id,
            )
        except SavingsGoalNotFoundError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_404_NOT_FOUND,
            )

        contributions = service.list_contributions_for_goal(
            goal=goal
        )

        return Response(
            SavingsContributionResponseSerializer(
                contributions,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, goal_id):
        serializer = SavingsContributionCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = self.service_provider()

        try:
            goal = service.get_for_user(
                user=request.user,
                goal_id=goal_id,
            )
        except SavingsGoalNotFoundError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            contribution = service.add_contribution(
                goal=goal,
                amount=serializer.validated_data["amount"],
                contribution_date=serializer.validated_data["date"],
            )
        except SavingsContributionDomainError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_409_CONFLICT,
            )


        response_data = SavingsContributionResponseSerializer(
            contribution
        ).data

        response_data["current_amount"] = str(
            goal.current_amount
        )
        response_data["remaining"] = str(
            service.calculate_remaining_amount(goal)
        )
        response_data["progress"] = str(
            round(service.calculate_progress(goal), 2)
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )