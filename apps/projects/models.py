from django.db import models
from django.conf import settings
from apps.organizations.models import Organization


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active',
        ON_HOLD = 'on_hold', 'On Hold',
        COMPLETED = 'completed', 'Completed',
        ARCHIVED = 'archived', 'Archived'

    # viewer => public , private
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public' # all org members can view
        PRIVATE = 'private', 'Private' #  only project members can view

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        related_name='projects',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_projects',
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'organization')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    

class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        PROJECT_MANAGER = 'project_manager', 'Project Manager'
        DEVELOPER = 'developer', 'Developer'
        VIEWER = 'viewer', 'Viewer'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='project_memberships',
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project,
        related_name='memberships',
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.role})"
    
class Sprint(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planned'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
    
    name = models.CharField(max_length=150)
    goal = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        Project,
        related_name='sprints',
        on_delete=models.CASCADE
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_sprints',
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"
    
    def dataValidate(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date.")
        