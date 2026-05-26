from django.db import models
from django.conf import settings

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='org_logos/',
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_organizations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now =True)


    def __str__(self):
        return self.name
    


class OrgMembership(models.Model):
    class Role(models.TextChoices):
        ORG_ADMIN = 'org_admin', 'Org Admin'
        PROJECT_MANAGER = 'project_manager', 'Project Manager'
        DEVELOPER = 'developer', 'Developer'
        VIEWER = 'viewer', 'Viewer'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name='org_memberships'
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DEVELOPER
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ('user', 'organization')
        ordering = ['-joined_at']
    

    def __str__(self):
        return f"{self.user.email} => {self.organization}"