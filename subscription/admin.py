from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
       Admin interface for managing Subscription objects.
       This class customizes how Subscription objects are displayed, filtered, and searched in the Django admin panel.
    """
    list_display = ('user__email', 'start_date', 'frequency', 'report_time')
    list_filter = ('frequency', 'start_date')
    search_fields = ('user__email', 'frequency')
    ordering = ('-start_date',)
