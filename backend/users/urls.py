from django.urls import path
from .views import (
    CSRFTokenView,
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    path('csrf/', CSRFTokenView.as_view(), name='csrf-token'), 
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),   
    path('admin/users/', UserListView.as_view(), name='user-list'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]