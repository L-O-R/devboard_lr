from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'date_joined', 'is_active')
    