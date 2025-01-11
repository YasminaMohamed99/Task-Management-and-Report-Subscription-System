from rest_framework.exceptions import PermissionDenied, NotFound, AuthenticationFailed
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Task
from ..serializers import TaskSerializer


class TaskOwnerMixin:
    """
    Mixin to ensure that only the task owner can access or modify tasks.
    Provides common query logic for tasks that are not deleted.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only tasks that are not marked as deleted.
        Restricted to tasks owned by the authenticated user.
        """
        return Task.objects.filter(is_deleted=False)

    def get_object(self):
        """
        Get the task object or raise 404 if not found, Check ownership to ensure only the task owner can update it.
        """
        # Explicit handling for unauthenticated users
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed()
        try:
            task = super().get_object()
        except:
            raise NotFound("Task with the given ID does not exist.")

        # Ensure that the current user is the owner of the task.
        if task.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this task.")

        return task