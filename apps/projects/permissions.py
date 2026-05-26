from rest_framework.permissions import BasePermission
from .models import ProjectMembership
from apps.organizations.models import OrgMembership

class IsProjectMember(BasePermission):
    # need to be a project member to view the project details

    message = "You must be a project member to access this project."

    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')

        if not project_id:
            return False

        return ProjectMembership.objects.filter(
            user = request.user,
            project_id = project_id
        ).exists()

class IsProjectManager(BasePermission):
    message = "You must be a project manager to perform this action."

    def has_permission(self, request, view):
        org_id = view.kwargs.get('org_id')
        return OrgMembership.objects.filter(
            user = request.user,
            organization_id = org_id,
            role = OrgMembership.Role.PROJECT_MANAGER,
            is_active = True
        ).exists() 


class isOrgMemberForProject(BasePermission):
    message = "You must be an organization member to access this project."

    def has_permission(self, request, view):
        org_id = view.kwargs.get('org_id')
        return OrgMembership.objects.filter(
            user = request.user,
            organization_id = org_id,
            is_active = True
        ).exists()