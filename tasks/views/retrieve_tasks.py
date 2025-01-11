from rest_framework.exceptions import AuthenticationFailed

from tasks.models import Task
from tasks.serializers import TaskSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from tasks.utils import filter_by_date_range


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter('status', description="Filter tasks by status.", type=str, required=False,
                             enum=["Pending", "Completed", "Overdue"]),
            OpenApiParameter('start_date', description="Filter tasks starting from this date (format: YYYY-MM-DD).",
                             type=str, required=False),
            OpenApiParameter('end_date', description="Filter tasks ending on or before this date (format: YYYY-MM-DD).",
                             type=str, required=False)
        ],
        tags=["Tasks"],
        responses={
            200: OpenApiResponse(description="Tasks retrieved successfully"),
            400: OpenApiResponse(description="Bad Request - Invalid date format. Use YYYY-MM-DD."),
            401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
            500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
        },
    )
)
class TaskListView(ListAPIView):
    """
    Retrieves a list of tasks filtered by the provided parameters or all tasks owned by the authenticated user.

    **Parameters:**

    - `status`: (Optional) Filter tasks by their status.
      Valid options:
      - `Pending`: Tasks that are pending.
      - `Completed`: Tasks that have been completed.
      - `Overdue`: Tasks that are overdue.

    - `start_date`: (Optional) Filter tasks that start on or after this date (format: YYYY-MM-DD).

    - `end_date`: (Optional) Filter tasks that end on or before this date (format: YYYY-MM-DD).
    This filter works as follows:
        - If a task has a `completion_date`, it will be included if the `completion_date` is
          less than or equal to the provided `end_date`.
        - If a task does not have a `completion_date` but has a `due_date`, it will be included
          if the `due_date` is less than or equal to the provided `end_date`.

    **Returns:**
    - A filtered list of tasks based on the provided parameters, or all tasks if no parameters are provided.
    - Returns a `400 Bad Request` response if invalid parameters are provided.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = Task.objects.filter(owner=user, is_deleted=False)

        # Filter by status
        if status_filter in ["Pending", "Completed", "Overdue"]:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        queryset = filter_by_date_range(queryset, start_date, end_date)

        return queryset

    def list(self, request, *args, **kwargs):
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()
        try:
            queryset = self.get_queryset()
            if isinstance(queryset, Response):
                return queryset

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
