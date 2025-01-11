from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from tasks.mixins.task_owner import TaskOwnerMixin
from tasks.models import Task
from tasks.serializers import TaskSerializer


@extend_schema(
    request=TaskSerializer,
    tags=["Tasks"],
    responses={
        200: OpenApiResponse(description="Task updated successfully."),
        400: OpenApiResponse(description="Bad Request - Invalid data provided or update failed."),
        401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
        403: OpenApiResponse(description="Permission Denied - You do not have permission to access this task."),
        404: OpenApiResponse(description="Task doesn't exist."),
        500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
    }
)
class TaskUpdateView(TaskOwnerMixin, UpdateAPIView):
    """
    Update an existing task.

    The task can only be updated by its owner. If the `status` field is changed to a completed or overdue status,
    the `completion_time` field will be automatically updated to the current date.

    **Validation Rules**:
    - `title` must be unique across all tasks for its owner.
    - `start_date` must be earlier than or equal to `due_date` and `completion_date` if exists.
    - Updated task by its owner.

    **Returns**:
    - A response returned according to status code.
    """
    def update(self, request, *args, **kwargs):
        """
        Override the update method to ensure only the task owner can update it.
        """
        try:
            task = self.get_object()
            partial = request.method == "PATCH"
            serializer = self.get_serializer(task, data=request.data, partial=partial, context={'user_request': request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ParseError as e:
            raise ParseError("Invalid JSON request format")

