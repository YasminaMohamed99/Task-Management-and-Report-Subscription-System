from django.contrib import admin
from .models import Task

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
        list_display: Specifies which fields are shown in the list view of the admin.
        list_filter: Adds filters to the right sidebar for filtering by specific fields.
        search_fields: Enables a search box to search by specified fields.
        ordering: Orders tasks by 'id' in the admin interface.
        fieldsets: Customize Form Display to organize fields into sections.
    """
    list_display = ('id', 'title', 'status', 'start_date', 'due_date', 'completion_date', 'owner_email','is_deleted', 'deleted_at', 'created_at','updated_at')
    list_filter = ('status', 'start_date', 'due_date', 'completion_date', 'is_deleted')
    search_fields = ('title', 'description', 'status', 'owner_email', 'is_deleted')
    ordering = ['id']
    fieldsets = (
        (None, {'fields': ('title', 'description', 'owner')}),
        ('Dates', {'fields': ('start_date', 'due_date', 'completion_date')}),
        ('Status', {'fields': ('status', 'is_deleted')}),
    )

    def owner_email(self, obj):
        return obj.owner.email