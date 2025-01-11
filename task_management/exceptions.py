from rest_framework.views import exception_handler
from rest_framework.exceptions import (AuthenticationFailed, NotFound, ValidationError, PermissionDenied, ParseError,
                                       NotAuthenticated)
from rest_framework import status


def custom_exception_handler(exc, context):
    """
        Custom exception handler to provide consistent error responses across different exception types.

        - Handles specific exceptions like AuthenticationFailed, NotFound, ValidationError, etc.
        - Provides tailored error messages for each type of exception.
        - For unexpected exceptions, a generic error response is returned.
        - If DRF's default exception handler doesn't generate a response, None is returned to allow default behavior.
    """
    # Call DRF's default exception handler to get a response
    response = exception_handler(exc, context)

    # If DRF did not generate a response, return None (use default behavior)
    if response is None:
        return None

    # Dictionary to store error messages for specific exceptions
    error_messages = {
        AuthenticationFailed: {
            "message": exc.detail if hasattr(exc,
                                             'detail') else "Your access token has expired or is invalid. Please log in again."
        },
        NotAuthenticated: {
            "message": exc.detail if hasattr(exc, 'detail') else "Authentication credentials were not provided."
        },
        NotFound: {
            "message": exc.detail if hasattr(exc, 'detail') else "The requested resource doesn't exist."
        },
        ValidationError: {
            "messages": exc.detail if hasattr(exc, 'detail') else "Invalid data."
        },
        PermissionDenied: {
            "message": exc.detail if hasattr(exc, 'detail') else "You do not have permission to perform this action."
        },
        ParseError: {
            "message": exc.detail if hasattr(exc, 'detail') else "Invalid Parsed data."
        },
    }

    # Check if the exception type is in our defined error messages
    print(type(exc))
    if type(exc) in error_messages:
        response.data = error_messages[type(exc)]
        # Set specific status codes for these exceptions
        if type(exc) in [AuthenticationFailed, NotAuthenticated]:
            response.status_code = status.HTTP_401_UNAUTHORIZED
        elif type(exc) == PermissionDenied:
            response.status_code = status.HTTP_403_FORBIDDEN
        elif type(exc) == NotFound:
            response.status_code = status.HTTP_404_NOT_FOUND
        elif type(exc) == ValidationError:
            response.status_code = status.HTTP_400_BAD_REQUEST
        elif type(exc) == ParseError:
            response.status_code = status.HTTP_400_BAD_REQUEST
    else:
        # Handle generic exceptions (fallback for unexpected errors)
        response.data = {
            "detail": "An unexpected error occurred.",
            "message": str(exc),
        }
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # if type(exc) in error_messages:
    #     response.data = error_messages[type(exc)]
    #
    # #Handle generic exceptions (fallback for unexpected errors)
    # elif isinstance(exc, Exception):
    #     response.data = {
    #         "detail": "An unexpected error occurred.",
    #         "message": str(exc),
    #     }
    #     response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return response
