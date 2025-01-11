from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tasks.serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated


@extend_schema(request=TaskSerializer, tags=["Tasks"],
               responses={
                   201: OpenApiResponse(description="Task Created successfully"),
                   400: OpenApiResponse(description="Bad Request - Invalid input data."),
                   401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
                   500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
               })
class TaskCreateView(APIView):
    """
       Creates a new task with the provided details.

       **Request Body**:
       - `title` (str): The title of the task. (Required)
       - `description` (str): A detailed description of the task. (Required)
       - `start_date` (date): The start date of the task (format: YYYY-MM-DD). (Required)
       - `due_date` (date): The due date of the task (format: YYYY-MM-DD). (Required)
       - `completion_date` (date): The date the task was completed (format: YYYY-MM-DD). (Optional)
       - `status` (str): The current status of the task. Options: ["Pending", "Completed", "Overdue"], and add "Pending" as a default (Optional)

       **Validation Rules**:
        - `title` must be unique across all tasks.
        - `start_date` must be earlier than or equal to `due_date` and `completion_date` if exists.

       **Returns**:
       - On success, returns the created task with status 201.
       - On failure, returns validation errors with status 400.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()
        try:
            serializer = TaskSerializer(data=request.data, context={'user_request': request.user})
            if serializer.is_valid():
                serializer.save(owner=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ParseError as e:
            raise ParseError("Invalid JSON request format")
