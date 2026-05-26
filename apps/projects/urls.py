from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectMemberView,
    SprintListCreateView,
    SprintDetailView
)

urlpatterns = [
    path('',
         ProjectListCreateView.as_view(),
         name='project-list-create'),

    path('<int:project_id>/',
         ProjectDetailView.as_view(),
         name='project-detail'),

    path('<int:project_id>/members/',
         ProjectMemberView.as_view(),
         name='project-members'),
         
    path('<int:project_id>/sprints/',
         SprintListCreateView.as_view(),
         name='sprint-list-create'),

    path('<int:project_id>/sprints/<int:sprint_id>/',
         SprintDetailView.as_view(),
         name='sprint-detail'),
]