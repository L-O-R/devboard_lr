
from django.urls import is_valid_path
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .permissions import (
    isOrgMemberForProject,
    IsProjectManager,
    IsProjectMember
)

from rest_framework.response import Response
from rest_framework import status, generics

from .serializers import (
    ProjectMembershipSerializer,
    ProjectSerializer,
    AddProjectMemberSerializer,
    SprintSerializer,
    ProjectMembershipSerializer
)

from django.db.models import Q

from .models import (
    ProjectMembership,
    Project,
    Sprint
)

from apps.accounts.models import User
from apps.organizations.models import OrgMembership
from apps.organizations.permissions import isOrgAdmin


class ProjectListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), isOrgMemberForProject() ]
        return [IsAuthenticated()]
    
    def get(self, request, org_id):
        user_project_ids = list(ProjectMembership.objects.filter(
            user = request.user
        ).values_list('project_id', flat=True)
        )

        projects = Project.objects.filter(
            organization_id = org_id
        ).filter(
            Q(visibility = Project.Visibility.PUBLIC) | 
            Q(id__in = user_project_ids)
        ).select_related('created_by', 'organization')
 

        serializers = ProjectSerializer(projects, many = True)
        return Response(serializers.data, status= status.HTTP_200_OK)
    
    def post(self, request, org_id):
        serializers = ProjectSerializer(data = request.data)
        if serializers.is_valid():
            project  = serializers.save(
                created_by = request.user,
                organization_id = org_id
            )

            #  user developer => project create => project manager
            ProjectMembership.objects.create(
                user = request.user,
                project = project,
                role = ProjectMembership.Role.PROJECT_MANAGER
            )

            return Response(
                ProjectSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)



class ProjectDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), IsProjectManager()]

    def get(self, request, org_id, project_id):
        project = get_object_or_404(
            Project, id=project_id, organization_id=org_id
        )
        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, org_id, project_id):
        project    = get_object_or_404(
            Project, id=project_id, organization_id=org_id
        )
        serializer = ProjectSerializer(
            project, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_id, project_id):
        project = get_object_or_404(
            Project, id=project_id, organization_id=org_id
        )
        project.delete()
        return Response(
            {'message': 'Project deleted!'},
            status=status.HTTP_204_NO_CONTENT
        )


class ProjectMemberView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), IsProjectManager()]

    def get(self, request, org_id, project_id):
        memberships = ProjectMembership.objects.filter(
            project_id=project_id
        ).select_related('user')           

        serializer = ProjectMembershipSerializer(memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, org_id, project_id):
        serializer = AddProjectMemberSerializer(data=request.data)

        if serializer.is_valid():
            email   = serializer.validated_data['email']
            role    = serializer.validated_data['role']
            user    = User.objects.get(email=email)
            project = get_object_or_404(Project, id=project_id)

            # must be org member first!
            if not OrgMembership.objects.filter(
                user=user,
                organization=project.organization,
                is_active=True
            ).exists():
                return Response(
                    {'error': 'User must be an org member first!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ProjectMembership.objects.filter(
                user=user, project=project
            ).exists():
                return Response(
                    {'error': 'User is already a project member!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ProjectMembership.objects.create(
                user=user, project=project, role=role
            )

            return Response(
                {'message': f'{email} added as {role}!'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Sprints ─────────────────────────────────────────────────────────

class SprintListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsProjectManager()]
        return [IsAuthenticated(), IsProjectMember()]

    def get(self, request, org_id, project_id):
        sprints = Sprint.objects.filter(
            project_id=project_id
        ).select_related('created_by')       

        serializer = SprintSerializer(sprints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, org_id, project_id):
        project    = get_object_or_404(Project, id=project_id)
        serializer = SprintSerializer(data=request.data)

        if serializer.is_valid():
            sprint = serializer.save(
                project    = project,
                created_by = request.user
            )
            return Response(
                SprintSerializer(sprint).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SprintDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), IsProjectManager()]

    def get(self, request, org_id, project_id, sprint_id):
        sprint = get_object_or_404(
            Sprint, id=sprint_id, project_id=project_id
        )
        return Response(
            SprintSerializer(sprint).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, org_id, project_id, sprint_id):
        sprint     = get_object_or_404(
            Sprint, id=sprint_id, project_id=project_id
        )
        serializer = SprintSerializer(
            sprint, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_id, project_id, sprint_id):
        sprint = get_object_or_404(
            Sprint, id=sprint_id, project_id=project_id
        )
        sprint.delete()
        return Response(
            {'message': 'Sprint deleted!'},
            status=status.HTTP_204_NO_CONTENT
        )

