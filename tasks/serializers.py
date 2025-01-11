from rest_framework import serializers
from datetime import datetime

from rest_framework.exceptions import PermissionDenied

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'start_date', 'due_date', 'completion_date', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        """
            Validate the task data before saving. This checks:
            - The start date cannot be after the due date.
            - The start date cannot be after the completion date.
            - The task title must be unique.
        """

        start_date = data.get('start_date', self.instance.start_date if self.instance else None)
        due_date = data.get('due_date', self.instance.due_date if self.instance else None)
        completion_date = data.get('completion_date', self.instance.completion_date if self.instance else None)
        owner = self.context.get('user_request', None)

        if not owner:
            raise serializers.ValidationError({"error": "An unexpected error occurred."})

        errors = []

        if start_date and due_date and start_date > due_date:
            errors.append("Start date cannot be after the due date.")

        if start_date and completion_date and start_date > completion_date:
            errors.append("Start date cannot be after the completion date.")

        if Task.objects.filter(owner=owner, title=data.get('title')).exclude(id=self.instance.id if self.instance else None).exists():
            errors.append("Title already exists for another task.")

        if errors:
            raise serializers.ValidationError({"errors": errors})

        return data
