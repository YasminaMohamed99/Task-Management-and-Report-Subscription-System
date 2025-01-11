from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import SignUpSerializer
from rest_framework.permissions import AllowAny


class SignUpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SignUpSerializer, tags=["User"],
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Bad Request - Validation errors"),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
        },
        examples=[
            OpenApiExample("Valid sign-up request example",
               value={
                     "username": "username",
                      "email": "user@example.com",
                      "password": "Password123"
               },
            )
        ]
    )
    def post(self, request):
        """
            This API allows users to sign up by providing a username, email, and password, and prevent duplicate sign-ups using the same email.\n
            The password is validated to ensure it meets the following security criteria:\n
                - Minimum Length: The password must be at least 8 characters long.
                - Contains a Digit: The password must contain at least one digit.
                - Contains a Lowercase Letter: The password must contain at least one lowercase letter.
                - Contains an Uppercase Letter: The password must contain at least one uppercase letter.
                - Contains a Special Character: The password must contain at least one special character (e.g., !, @, #, etc.).
            """
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
