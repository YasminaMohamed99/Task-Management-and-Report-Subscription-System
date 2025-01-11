from django.urls import path
from tasks.views.create_task import TaskCreateView
from tasks.views.retrieve_tasks import TaskListView
from tasks.views.update_task import TaskUpdateView
from tasks.views.delete_task import TaskDeleteView
from tasks.views.restore_task import TaskRestoreView
from tasks.views.batch_delete import TaskBatchDeleteView

urlpatterns = [
    path('retrieve_tasks/', TaskListView.as_view(), name='retrieve-tasks'),
    path('create/', TaskCreateView.as_view(), name='create-task'),
    path('update/<int:pk>/', TaskUpdateView.as_view(), name='update-task'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='delete-task'),
    path('restore/', TaskRestoreView.as_view(), name='task-restore'),
    path('batch-delete/', TaskBatchDeleteView.as_view(), name='batch-delete'),
]
