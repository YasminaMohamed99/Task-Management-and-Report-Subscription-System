import re
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


# Custom password validator
def validate_password_strength(password):
    """
       Validates the strength of the provided password.

       The password must contain:
       - At least one digit
       - At least one lowercase letter
       - At least one uppercase letter
       - At least one special character
       - A minimum length of 8 characters
    """
    errors = []

    # Check if password contains at least one digit
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    # Check if password contains at least one lowercase letter
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    # Check if password contains at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    # Check if password contains at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    # Check if password length is at least 8 characters
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if errors:
        raise serializers.ValidationError(errors)


class SignUpSerializer(serializers.ModelSerializer):
    """
       Serializer for signing up a new user.
       Validates the user's email and password, ensuring the email doesn't duplicate
       and the password meets security requirements before creating a new user.
    """
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already registered.")])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password_strength])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Automatically hashes the password before saving it
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
        return user

class SignInSerializer(serializers.Serializer):
    """
        Serializer for user sign-in.
        Validates the email and password provided during the login process.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

