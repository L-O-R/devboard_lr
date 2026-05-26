

from django.db import models
from django.conf import settings
from apps.projects.models import   Project, Sprint

class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#f5f5f5')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name = 'labels'
    )

    class Meta:
        unique_together = ['name','project'] 
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"
    

class Task(models.Model):
    class Status(models.TextChoices):
        BACKLOG = 'backlog', 'Backlog'
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In Progress'
        IN_REVIEW = 'in_review', 'In Review'
        DONE = 'done', 'Done'
    
    class Priority(models.TextChoices):
        LOW = 'low' , 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'
    
    title = models.CharField(max_length = 255)
    description = models.TextField(null = True, blank= True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name = 'tasks'
    )

    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name = 'tasks'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_tasks',
        on_delete=models.SET_NULL,
        null=True
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank = True,
        related_name = 'assigned_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    labels = models.ManyToManyField(
        Label,
        related_name='tasks',
        blank=True
    )

    due_data = models.DateField(null= True, blank=True)
    order = models.PositiveBigIntegerField (default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)