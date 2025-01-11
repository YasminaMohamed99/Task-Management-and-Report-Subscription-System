from django.db import models
from django.conf import settings


# Create your models here.


class Task(models.Model):
    # Choices for the status field to represent different task states
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    due_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_deleted = models.BooleanField(default=False)  # Soft delete
    # Stores the timestamp when the task is marked as deleted to restore last deleted task
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure that the title is unique for each user (owner).
        constraints = [
            models.UniqueConstraint(fields=['owner', 'title'], name='unique_task_title_for_user')
        ]

    def __str__(self):
        return self.title
