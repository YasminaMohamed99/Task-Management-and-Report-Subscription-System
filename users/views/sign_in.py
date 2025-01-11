from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from datetime import datetime
from users.serializers import SignInSerializer
from rest_framework_simplejwt.views import TokenRefreshView


@extend_schema(
    request=SignInSerializer, tags=["User"],
    responses={
            200: OpenApiResponse(description="Login Successfully"),
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="User Unauthorized"),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
        },
)
class SignInView(APIView):
    """
        API endpoint for user sign-in.

        Authenticates a user using email and password. If the credentials are valid, it generates a JWT access token and
        a refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Use the SignInSerializer to validate the input data
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

            user = authenticate(username=user.username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                expiration_time = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

                return Response({"refresh": str(refresh), "access": access_token, "access_token_expiration": expiration_time}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['User'],
    responses={200: 'New access token', 400: 'Bad Request - Invalid refresh token'},
)
class TokenRefreshViewWithCustomResponse(TokenRefreshView):
    """
    Token refresh view for getting a new access token using the refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Call the TokenRefreshView to get a new access token
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            return Response({
                'access': response.data['access']
            })
        return response

