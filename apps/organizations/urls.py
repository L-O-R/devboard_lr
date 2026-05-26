from django.urls import path
from .views import (
    OrganizationListCreateView,
    OrganiztionDetailView,
    OrgMembersListView,
    InviteMemberView,
    RemoveMemberView
)

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='org-list-create'),
    path('<int:org_id>/', OrganiztionDetailView.as_view(), name = 'org-detail'),
    path('<int:org_id>/members/', OrgMembersListView.as_view(), name='org-members-list'),
    path('<int:org_id>/invite/', InviteMemberView.as_view(), name='invite-member'),
    path('<int:org_id>/members/<int:user_id>/remove/', RemoveMemberView.as_view(), name='remove-member'),
]