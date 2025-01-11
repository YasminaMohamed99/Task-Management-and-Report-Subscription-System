from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    """
       Model representing a subscription for generating reports.

       Attributes:
           user (User): The user who owns the subscription.
           start_date (DateTimeField): The start date and time for the subscription.
           frequency (CharField): The frequency at which reports should be generated (daily, weekly, or monthly).
           report_time (PositiveSmallIntegerField): The hour of the day (0-23) when the report should be generated.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    frequency = models.CharField(max_length=7, choices=FREQUENCY_CHOICES)
    report_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text="Hour of the day for report generation (0-23)."
    )

    def __str__(self):
        return f"Subscription for {self.user}"