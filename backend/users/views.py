import logging
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserListSerializer
)
from .models import User
from .permissions import IsAdminUser

logger = logging.getLogger(__name__)


class CSRFTokenView(APIView):
    """Получение CSRF токена."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token})


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f'Новый пользователь зарегистрирован: {user.username}')
            
            return Response({
                'message': 'Регистрация успешна',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        logger.warning(f'Ошибка регистрации: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Вход в систему."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            logger.info(f'Пользователь вошел в систему: {user.username}')
            
            return Response({
                'message': 'Вход выполнен успешно',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        logger.warning(f'Ошибка входа: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Выход из системы."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.user.username if request.user.is_authenticated else 'anonymous'
        
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
        
        logger.info(f'Пользователь вышел из системы: {username}')
        
        return Response({
            'message': 'Выход выполнен успешно'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """Получение данных текущего пользователя."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """Список всех пользователей (только для админов)."""
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали пользователя (только для админов)."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()
    
    def update(self, request, *args, **kwargs):
        """Обновление пользователя (например, изменение is_admin)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        allowed_fields = {'is_admin'}
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f'Админ {request.user.username} обновил пользователя {instance.username}')
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Удаление пользователя."""
        instance = self.get_object()
        username = instance.username
        
        instance.delete()
        
        logger.info(f'Админ {request.user.username} удалил пользователя {username}')
        
        return Response(status=status.HTTP_204_NO_CONTENT)