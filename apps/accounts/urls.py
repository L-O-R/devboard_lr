from django.urls import path

from .views import (
    RegisterVIEW,
    LoginView,
    LogoutView,
    ProfileView
)

urlpatterns = [
    path('register', RegisterVIEW.as_view(), name = 'register'),
    path('login', LoginView.as_view(), name = 'login'),
    path('logout', LogoutView.as_view(), name = 'logout'),
    path('profile', ProfileView.as_view(), name = 'profile'),
]