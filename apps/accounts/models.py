from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ORG_ADMIN = 'org_admin', 'Org Admin'
        PROJECT_MANAGER = 'project_manager', 'Project Manager'
        DEVELOPER = 'developer', 'Developer'
        VIEWER = 'viewer', 'Viewer'
    
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    bio = models.TextField(null = True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def is_org_admin(self):
        return self.role == self.Role.ORG_ADMIN
    
    @property
    def is_project_manager(self):
        return self.role == self.Role.PROJECT_MANAGER
    
