from rest_framework import serializers
from .models import Task, Label
from apps.accounts.serializers import UserProfileSerializer
from apps.projects.models import ProjectMembership, Sprint
from apps.accounts.models import User


class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = ['id', 'name', 'color', 'project']
        read_only_fields = ['id', 'project']


class TaskSerializer(serializers.ModelSerializer):

    created_by = UserProfileSerializer(read_only=True)
    assigned_to = UserProfileSerializer(read_only=True)
    labels = LabelSerializer(read_only=True, many=True)

    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.none(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True
    )

    label_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.none(),
        source='labels',
        many=True,
        write_only=True,
        required=False
    )

    sprint_id = serializers.PrimaryKeyRelatedField(
        queryset=Sprint.objects.none(),
        source='sprint',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description',
            'project', 'sprint', 'sprint_id',
            'assigned_to', 'assigned_to_id',
            'created_by', 'status', 'priority',
            'labels', 'label_ids',
            'due_date', 'order',
            'created_at', 'updated_at'
        ]

        read_only_fields = [
            'id', 'project', 'created_by',
            'created_at', 'updated_at'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        view = self.context.get('view')

        if view:
            project_id = view.kwargs.get('project_id')

            member_ids = ProjectMembership.objects.filter(
                project_id=project_id
            ).values_list('user_id', flat=True)

            self.fields['assigned_to_id'].queryset = User.objects.filter(
                id__in=member_ids
            )

            self.fields['label_ids'].queryset = Label.objects.filter(
                project_id=project_id
            )

            self.fields['sprint_id'].queryset = Sprint.objects.filter(
                project_id=project_id
            )

    def validate(self, attrs):

        sprint = attrs.get('sprint')
        status = attrs.get('status')

        if (
            sprint and
            sprint.status == 'planning' and
            status == Task.Status.DONE
        ):
            raise serializers.ValidationError(
                "Cannot mark task as Done in a Planning sprint!"
            )

        return attrs
    

class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Lightweight serializer — only for status updates by developers."""

    class Meta:
        model  = Task
        fields = ['status']

    def validate_status(self, value):
        # get current task status
        current = self.instance.status if self.instance else None

        # define allowed transitions
        allowed_transitions = {
            Task.Status.BACKLOG:     [Task.Status.TODO],
            Task.Status.TODO:        [Task.Status.IN_PROGRESS],
            Task.Status.IN_PROGRESS: [Task.Status.IN_REVIEW, Task.Status.TODO],
            Task.Status.IN_REVIEW:   [Task.Status.DONE, Task.Status.IN_PROGRESS],
            Task.Status.DONE:        [Task.Status.IN_REVIEW],  # can reopen
        }

        if current and value not in allowed_transitions.get(current, []):
            raise serializers.ValidationError(
                f"Cannot move task from '{current}' to '{value}'!"
            )
        return value