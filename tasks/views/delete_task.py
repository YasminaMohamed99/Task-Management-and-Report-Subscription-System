from rest_framework.generics import DestroyAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from tasks.mixins.task_owner import TaskOwnerMixin


@extend_schema(
    tags=["Tasks"],
    responses={
        204: OpenApiResponse(description="Task deleted successfully."),
        400: OpenApiResponse(description="Bad Request - Invalid task ID."),
        401: OpenApiResponse(description="Unauthorized User - Authentication credentials were not provided."),
        403: OpenApiResponse(description="Permission Denied - You do not own this task."),
        404: OpenApiResponse(description="Task doesn't exist."),
        500: OpenApiResponse(description="Internal Server Error - An unexpected error occurred."),
    }
)
class TaskDeleteView(TaskOwnerMixin, DestroyAPIView):
    """
    Soft delete a task by its ID.

    Only the task owner can delete the task. If the task is already deleted or not found,
    a 404 Not Found error will be returned.
    """

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance