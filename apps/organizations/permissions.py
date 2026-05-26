from rest_framework.permissions import BasePermission
from .models import OrgMembership


class isOrgAdmin(BasePermission):
    message = "You must be an Org Amin to Perform this action or whatever"
    def has_permission(self, request, view):
        org_id= view.kwargs.get('org_id')

        if not org_id:
            return False
        
        return OrgMembership.objects.filter(
            user = request.user,
            organization_id = org_id,
            role = OrgMembership.Role.ORG_ADMIN,
            is_active = True
        ).exists()
    

class IsOrgMember(BasePermission):
    message = "You are not a member of this organization, Request Admin"

    def has_permission(self, request, view):
        org_id= view.kwargs.get('org_id')

        if not org_id:
            return False
        
        return OrgMembership.objects.filter(
            user = request.user,
            organization_id = org_id,
            is_active = True
        ).exists()