from rest_framework.permissions import BasePermission
from apps.projects.models import ProjectMembership

class IsTaskProjectMember(BasePermission):
    message = "You are not a memeber of this project"

    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')
        print("----------------------------------------------------------------")
        print(request.user)
        return ProjectMembership.objects.filter(
            
            user = request.user,
            project_id = project_id
        ).exists()
    

class CanManageTask(BasePermission):
     message = "You are not a PM of this project"

     def has_permission(self, request, view):
         from rest_framework.permissions import SAFE_METHODS

         project_id = view.kwargs.get('project_id')
         membership = ProjectMembership.objects.filter(
             user_id = request.user_id,
            project_id = project_id
         ).first()
         if not membership:
             return False
         
         if membership.role == ProjectMembership.Role.VIEWER:
             request.method in SAFE_METHODS

         return True