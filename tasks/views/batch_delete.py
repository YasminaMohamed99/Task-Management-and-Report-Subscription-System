from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from tasks.models import Task
from django.utils import timezone

from tasks.utils import filter_by_date_range


# Applying the extend_schema_view decorator to the entire view class
@extend_schema_view(
    delete=extend_schema(
        parameters=[
            OpenApiParameter('start_date', description="Filter tasks starting from this date (format: YYYY-MM-DD).", type=str, required=False),
            OpenApiParameter('end_date', description="Filter tasks ending on or before this date (format: YYYY-MM-DD).", type=str, required=False)
        ],
        tags=["Tasks"],
        responses={
            204: OpenApiResponse(description="Tasks successfully deleted."),
            400: OpenApiResponse(description="Bad Request - Invalid date format. Use YYYY-MM-DD."),
            401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
            404: OpenApiResponse(description="No tasks found in the given date range."),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred.")
        }
    )
)
class TaskBatchDeleteView(APIView):
    """
        Batch delete tasks within a specified date range.
        If no date range is provided, all tasks of the authenticated user will be deleted.

        It checks for a valid `start_date` and `end_date` in the query parameters, filters the tasks
        by these dates, and marks them as deleted. If no tasks are found, it returns a 404 error.

       **Parameters:**
        - `start_date`: (Optional) Filter tasks that start on or after this date (format: YYYY-MM-DD).

        - `end_date`: (Optional) Filter tasks that end on or before this date (format: YYYY-MM-DD).
        This filter works as follows:
            - If a task has a `completion_date`, it will be included if the `completion_date` is
              less than or equal to the provided `end_date`.
            - If a task does not have a `completion_date` but has a `due_date`, it will be included
              if the `due_date` is less than or equal to the provided `end_date`.

        **Returns**:
        - A response returned according to status code.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Soft delete tasks within the given date range
        tasks = Task.objects.filter(owner=request.user, is_deleted=False)
        tasks = filter_by_date_range(tasks, start_date, end_date)

        if tasks.exists():
            tasks.update(is_deleted=True, deleted_at=timezone.now())
            return Response({"message": f"{tasks.count()} tasks deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "No tasks found within the given date range."}, status=status.HTTP_404_NOT_FOUND)
