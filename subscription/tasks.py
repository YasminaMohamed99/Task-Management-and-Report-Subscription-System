from datetime import timedelta, datetime
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Subscription
from tasks.models import Task


@shared_task
def generate_report():
    """
       Celery task to generate and send task reports for active subscriptions.
       The task runs hourly and checks if a report should be sent based on the subscription's frequency.
    """
    time_now = datetime.now()
    # Filter subscriptions that started before or at the current time and match the current hour for report time
    subscriptions = Subscription.objects.filter(start_date__lte=time_now, report_time=time_now.hour)
    for subscription in subscriptions:
        should_send_report = check_frequency(subscription, time_now)
        if should_send_report:
            # Determine the start time for filtering tasks based on the subscription's frequency
            start_time_for_get_tasks = subscribed_period(subscription, time_now)

            # Retrieve tasks that are not deleted and fall within the specified time range
            tasks = Task.objects.filter(owner=subscription.user, is_deleted=False, due_date__range=[start_time_for_get_tasks, time_now])
            tasks_list = tasks.values('title', 'status', 'start_date', 'due_date', 'completion_date', )

            # Render the task report using an HTML template
            task_report = render_to_string('report_template.html', {'tasks': tasks_list})

            # Send the generated report via email
            send_report_email(subscription, task_report)


def check_frequency(subscription, time_now):
    """
        Determines whether a report should be sent for a given subscription
        based on its specified frequency (daily, weekly, or monthly).

        Logic:
            1. **Daily frequency**:
               - Always returns True, meaning a report is sent every day.
               - The filtering logic ensures that only subscriptions with the correct
                 report time are processed.

            2. **Weekly frequency**:
               - Sends the report on the same day of the week as the subscription's
                 start date (`start_date.weekday()`), ensuring that the report is sent
                 once per week on the correct day.

            3. **Monthly frequency**:
               - Sends the report on the same day of the month as the subscription's
                 start date (`start_date.day`).
               - Handles cases where the start day might not exist in the current month
                 (e.g., 31st in a month with fewer days) by sending the report on the
                 last day of the month if necessary.
    """

    if subscription.frequency == 'daily':
        return True
    # Send if today matches the start_date's weekday
    elif subscription.frequency == 'weekly':
        return subscription.start_date.weekday() == time_now.weekday()
    elif subscription.frequency == 'monthly':
        # Handle case where start day might not exist in the current month
        start_day = subscription.start_date.day
        last_day_of_current_month = (time_now + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        # If the start day is less than or equal to the last day of the month, check for an exact match
        if start_day <= last_day_of_current_month.day:
            return start_day == time_now.day
        else:
            # If the start day doesn't exist in this month, send the report on the last day of the month
            return time_now.day == last_day_of_current_month.day
    else:
        return False


def subscribed_period(subscription, time_now):
    """
       Calculates the start time for filtering tasks based on the subscription's frequency.
       Returns: The calculated start time for filtering tasks.
    """
    if subscription.frequency == 'daily':
        # For daily frequency, filter tasks that have a due date in the last 24 hours
        return time_now - timedelta(days=1)
    elif subscription.frequency == 'weekly':
        # For weekly frequency, filter tasks that have a due date in the last 7 days
        return time_now - timedelta(weeks=1)
    elif subscription.frequency == 'monthly':
        # For monthly frequency, filter tasks that have a due date in the last 30 days
        return time_now - timedelta(days=30)


def send_report_email(subscription, task_report):
    # Sends a task report email to the user associated with the subscription.
    try:
        send_mail(f'Your Tasks Report: {subscription.frequency} Update', '', 'yasmina.mohamed20399@gmail.com', [subscription.user.email], html_message=task_report,
                  fail_silently=False)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
