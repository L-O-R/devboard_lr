
from rest_framework.views import APIView
from rest_framework.response  import Response
from rest_framework   import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts   import get_object_or_404
from django.db.models import Q

from .models import Task, Label
from .serializers  import (
    TaskSerializer,
    TaskStatusUpdateSerializer,
    LabelSerializer
)
from .permissions  import IsTaskProjectMember, CanManageTask
from apps.projects.models import Project, ProjectMembership, Sprint



class LabelListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTaskProjectMember]

    def get(self, request, org_id, project_id):
        labels     = Label.objects.filter(project_id=project_id)
        serializer = LabelSerializer(labels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, org_id, project_id):
        project    = get_object_or_404(Project, id=project_id)
        serializer = LabelSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTaskProjectMember]

    def get(self, request, org_id, project_id):
        tasks = Task.objects.filter(
            project_id=project_id
        ).select_related(         
            'assigned_to',
            'created_by',
            'sprint'
        ).prefetch_related(         
            'labels'
        )

        sprint_id   = request.query_params.get('sprint_id')
        assigned_id = request.query_params.get('assigned_to')
        task_status = request.query_params.get('status')
        priority    = request.query_params.get('priority')
        search      = request.query_params.get('search')

        if sprint_id == 'backlog':
            tasks = tasks.filter(sprint__isnull=True)
        elif sprint_id:
            tasks = tasks.filter(sprint_id=sprint_id)

        if assigned_id:
            tasks = tasks.filter(assigned_to_id=assigned_id)

        if task_status:
            tasks = tasks.filter(status=task_status)

        if priority:
            tasks = tasks.filter(priority=priority)

        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        serializer = TaskSerializer(
            tasks, many=True, context={'request': request, 'view': self}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, org_id, project_id):
        project    = get_object_or_404(Project, id=project_id)
        serializer = TaskSerializer(
            data    = request.data,
            context = {'request': request, 'view': self}
        )

        if serializer.is_valid():
            task = serializer.save(
                project    = project,
                created_by = request.user
            )
            return Response(
                TaskSerializer(task, context={'request': request, 'view': self}).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated, CanManageTask]

    def get_task(self, project_id, task_id):
        return get_object_or_404(
            Task.objects.select_related(
                'assigned_to', 'created_by', 'sprint'
            ).prefetch_related('labels'),
            id         = task_id,
            project_id = project_id
        )

    def get(self, request, org_id, project_id, task_id):
        task = self.get_task(project_id, task_id)
        serializer = TaskSerializer(
            task, context={'request': request, 'view': self}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, org_id, project_id, task_id):
        task       = self.get_task(project_id, task_id)
        membership = ProjectMembership.objects.get(
            user=request.user, project_id=project_id
        )

        if membership.role == ProjectMembership.Role.DEVELOPER:
            serializer = TaskStatusUpdateSerializer(
                task, data=request.data, partial=True
            )
        else:
            serializer = TaskSerializer(
                task,
                data    = request.data,
                partial = True,
                context = {'request': request, 'view': self}
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                TaskSerializer(
                    task, context={'request': request, 'view': self}
                ).data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, org_id, project_id, task_id):
        task       = self.get_task(project_id, task_id)
        membership = ProjectMembership.objects.get(
            user=request.user, project_id=project_id
        )

        if membership.role != ProjectMembership.Role.PROJECT_MANAGER:
            return Response(
                {'error': 'Only Project Manager can delete tasks!'},
                status=status.HTTP_403_FORBIDDEN
            )

        task.delete()
        return Response(
            {'message': 'Task deleted!'},
            status=status.HTTP_204_NO_CONTENT
        )


class MyTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(
            assigned_to = request.user
        ).select_related(
            'project', 'sprint', 'created_by'
        ).prefetch_related(
            'labels'
        ).order_by('due_date', '-priority')

        serializer = TaskSerializer(
            tasks, many=True, context={'request': request, 'view': self}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)