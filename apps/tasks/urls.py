

from django.urls import path
from .views import (
    LabelListCreateView,
    TaskListCreateView,
    TaskDetailView,
    MyTasksView
)

urlpatterns = [
    path('labels/',
         LabelListCreateView.as_view(),
         name='label-list-create'),

    path('tasks/',
         TaskListCreateView.as_view(),
         name='task-list-create'),

    path('tasks/<int:task_id>/',
         TaskDetailView.as_view(),
         name='task-detail'),
]