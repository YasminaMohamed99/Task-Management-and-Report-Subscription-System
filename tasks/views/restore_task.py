from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from tasks.models import Task

@extend_schema(
    tags=["Tasks"],
    responses={
        200: OpenApiResponse(description="Last deleted task restored successfully"),
        401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
        404: OpenApiResponse(description="No deleted tasks found."),
        500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
    }
)
class TaskRestoreView(APIView):
    """
       Restore the last deleted task for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Explicit handling for unauthenticated users
        if not request.user.is_authenticated:
            raise AuthenticationFailed()
        try:
            task = Task.objects.filter(owner=request.user, is_deleted=True).exclude(deleted_at=None).order_by('-deleted_at').first()

            if task:
                task.is_deleted = False
                task.save()
                return Response({"message": "Last deleted task restored."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No deleted tasks found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
