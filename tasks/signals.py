from datetime import datetime
from django.db.models.signals import pre_save
from django.dispatch import receiver
from tasks.models import Task


@receiver(pre_save, sender=Task)
def set_deleted_at(sender, instance, **kwargs):
    """
       Automatically update the deleted_at field when is_deleted is set to True and
       set the completion_date field if the task's status is set to 'Completed' or 'Overdue'.
    """
    # Handle the deleted_at field
    if instance.is_deleted and not instance.deleted_at:
        instance.deleted_at = datetime.now()  # Set the deleted_at field to current time
    elif not instance.is_deleted:
        instance.deleted_at = None  # Reset deleted_at if is_deleted is False

    # Handle the completion_date field
    if instance.status in ["Completed", "Overdue"] and not instance.completion_date:
        # Automatically set completion_date if status is 'Completed' or 'Overdue'
        instance.completion_date = datetime.now().date()  # Set the completion_date to the current date
