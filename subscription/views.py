from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscription
from .serializers import SubscriptionSerializer


@extend_schema_view(
    # POST method: User subscribe
    post=extend_schema(request=SubscriptionSerializer,  # Request body should match the SubscriptionSerializer schema
        tags=["Subscriptions"], # Categorizes the endpoint under "Subscriptions"
        responses={
            200: OpenApiResponse(description="User is already subscribed."),
            201: OpenApiResponse(description="User has been successfully subscribed."),
            400: OpenApiResponse(description="Bad Request - Invalid input data."),
            401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
        },
       examples=[
           OpenApiExample("Valid subscription request example",
               value={
                   "start_date": "2025-01-01 09:00:00",  # Valid date-time format
                   "frequency": "weekly",  # One of the valid values: 'daily', 'weekly', 'monthly'
                   "report_time": "09:00"  # Valid 24-hour format: 'HH:MM'
               },
           )
       ]
    ),
    # DELETE method: User unsubscribe
    delete=extend_schema(tags=["Subscriptions"],
        responses={
            200: OpenApiResponse(description="User has been successfully unsubscribed."),
            401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
            404: OpenApiResponse(description="No active subscription found"),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
        },
    )
)
class SubscribeView(APIView):
    """
       This view handles subscribing and unsubscribing users to a subscription service.

       - POST method: Creates a new subscription for the authenticated user, or confirms an existing subscription.
       - DELETE method: Unsubscribes the authenticated user if they have an active subscription.
    """
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def post(self, request, *args, **kwargs):
        """
           Subscribes the user or confirms an existing subscription.

           - If the user is not already subscribed, a new subscription is created with the provided data.
           - If the user is already subscribed, a message indicating that is returned.

            **Request Body**:
            - `start_time` : Date of the report generation starts. (Required)
            - `frequency` : One of daily, weekly, monthly. (Required)
            - `report_time`: Time of the day for report generation. (Required)

           **Validation Roles:**
            - `start_date`:
                - Must be in the format 'YYYY-MM-DD HH:00:00'.
                - Example: "2025-01-01 09:00:00"

            - `frequency`:
                - Must be one of the following values: 'daily', 'weekly', 'monthly'.

            - `report_time`:
                - Must be in a valid time format of 'H:00:00', 'H:00', 'H', H (24-hour format) or 'H AM/PM'.
                - Example: "9 AM", "9PM", "09:00:00","18:00", "18", 18 (24-hour format).

           **Responses:**
           - 201: Successfully subscribed
           - 200: Already subscribed
           - 400: Bad Request (invalid data)
        """
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()

        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            # Try to get or create a subscription for the user
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'start_date': serializer.validated_data['start_date'],
                    'frequency': serializer.validated_data['frequency'],
                    'report_time': serializer.validated_data['report_time']
                }
            )
            if created:
                return Response({"message": "Subscribed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Already subscribed"}, status=status.HTTP_200_OK)
        # If the serializer is invalid, return the validation errors with a 400 status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
           Unsubscribe the user if you have an active subscription.

           **Responses:**
           - 200: Successfully unsubscribed
           - 404: No active subscription found
        """
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()

        try:
            # Retrieve the user's active subscription and delete it
            subscription = Subscription.objects.get(user=request.user)
            subscription.delete()
            return Response({"message": "Unsubscribed successfully"}, status=status.HTTP_200_OK)
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found"}, status=status.HTTP_404_NOT_FOUND)
