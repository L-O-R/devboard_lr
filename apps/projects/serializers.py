from rest_framework import serializers
from .models import Project, ProjectMembership, Sprint

from apps.accounts.serializers import UserProfileSerializer


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only = True)

    class Meta:
        model = ProjectMembership
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'user', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only = True)
    member_count = serializers.SerializerMethodField()
    sprint_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'visibility',
            'start_date', 'end_date', 'created_by', 'member_count',
            'sprint_count' ,'created_at', 'updated_at'
        ]
        read_only_fields = ['id','organization', 'created_by', 'created_at']

    def get_member_count(self, obj):
        return obj.memberships.count()

    def get_sprint_count(self, obj):
        return obj.sprints.count()


class SprintSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer(read_only = True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = [
            'id', 'name', 'goal', 'project', 'status',
            'start_date', 'end_date', 'created_by', 'task_count',
            'created_at'
        ]
        read_only_fields = ['id', 'project', 'created_by', 'created_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "End date cannot be before start date!"
            )
        return data
    
class AddProjectMemberSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only = True)

    class Meta:
        model = ProjectMembership
        fields = ['email', 'role']
    
    def validate_email(self, value):
        from apps.accounts.models import User
        if not User.objects.filter(email = value).exists():
            raise serializers.ValidationError(
                "No user found with this email!"
            )
        return value
    