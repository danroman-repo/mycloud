import logging
import os
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import File
from .serializers import (
    FileSerializer,
    FileUploadSerializer,
    FileRenameSerializer,
    FileCommentSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrSelf

logger = logging.getLogger(__name__)


class FileListView(generics.ListAPIView):
    """
    Получение списка файлов пользователя.
    
    Обычный пользователь видит только свои файлы.
    Администратор может видеть файлы любого пользователя (параметр ?user_id=123).
    """
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    
    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get('user_id')
        
        if user.is_admin and user_id:
            logger.info(f'Админ {user.username} запрашивает файлы пользователя {user_id}')
            return File.objects.filter(owner_id=user_id).order_by('-uploaded_at')
        
        logger.debug(f'Пользователь {user.username} запрашивает свои файлы')
        return File.objects.filter(owner=user).order_by('-uploaded_at')


class FileUploadView(generics.CreateAPIView):
    """Загрузка нового файла в хранилище."""
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            file_instance = serializer.save()
            logger.info(
                f'Пользователь {request.user.username} загрузил файл: '
                f'{file_instance.original_name} (размер: {file_instance.size} байт)'
            )
            
            return Response(
                FileSerializer(file_instance, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        logger.warning(f'Ошибка загрузки файла: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение деталей файла, обновление комментария, удаление файла.
    """
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = File.objects.all()
    
    def update(self, request, *args, **kwargs):
        """Обновление комментария к файлу."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = FileCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance.comment = serializer.validated_data.get('comment', '')
        instance.save()
        
        logger.info(
            f'Пользователь {request.user.username} обновил комментарий к файлу: '
            f'{instance.display_name}'
        )
        
        return Response(FileSerializer(instance, context={'request': request}).data)
    
    def destroy(self, request, *args, **kwargs):
        """Удаление файла."""
        instance = self.get_object()
        file_path = instance.file.path
        display_name = instance.display_name
        
        instance.delete()

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f'Файл удален с диска: {file_path}')
            except Exception as e:
                logger.error(f'Ошибка удаления файла с диска: {e}')
        
        logger.info(
            f'Пользователь {request.user.username} удалил файл: {display_name}'
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class FileRenameView(APIView):
    """Переименование файла."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def put(self, request, pk):
        file_instance = get_object_or_404(File, pk=pk)
        
        # Проверяем права доступа
        self.check_object_permissions(request, file_instance)
        
        serializer = FileRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_name = file_instance.display_name
        new_name = serializer.validated_data['display_name']
        
        file_instance.display_name = new_name
        file_instance.save()
        
        logger.info(
            f'Пользователь {request.user.username} переименовал файл: '
            f'{old_name} -> {new_name}'
        )
        
        return Response(FileSerializer(file_instance, context={'request': request}).data)


class FileDownloadView(APIView):
    """Скачивание файла (с обновлением last_downloaded_at)."""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get(self, request, pk):
        file_instance = get_object_or_404(File, pk=pk)
        
        self.check_object_permissions(request, file_instance)
        
        file_instance.last_downloaded_at = timezone.now()
        file_instance.save(update_fields=['last_downloaded_at'])
        
        if not os.path.exists(file_instance.file.path):
            logger.error(f'Файл не найден на диске: {file_instance.file.path}')
            raise Http404('Файл не найден')
        
        logger.info(
            f'Пользователь {request.user.username} скачал файл: {file_instance.display_name}'
        )

        view_mode = request.GET.get('view') == '1'
        can_view_inline = file_instance.mime_type in settings.VIEWABLE_MIME_TYPES
        as_attachment = not (view_mode and can_view_inline)

        response = FileResponse(
            open(file_instance.file.path, 'rb'),
            as_attachment=as_attachment,
            content_type=file_instance.mime_type
        )

        if as_attachment:
            response['Content-Disposition'] = f'attachment; filename="{file_instance.original_name}"'
        
        return response


class FileShareView(APIView):
    """
    Генерация/регенерация публичной ссылки на файл.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def post(self, request, pk):
        import uuid
        file_instance = get_object_or_404(File, pk=pk)
        
        self.check_object_permissions(request, file_instance)
        
        file_instance.public_hash = uuid.uuid4()
        file_instance.save(update_fields=['public_hash'])
        
        logger.info(
            f'Пользователь {request.user.username} сгенерировал новую публичную ссылку '
            f'для файла: {file_instance.display_name}'
        )
        
        return Response(FileSerializer(file_instance, context={'request': request}).data)


class PublicFileDownloadView(APIView):
    """
    Скачивание файла по публичной ссылке (без аутентификации).
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, public_hash):
        file_instance = get_object_or_404(File, public_hash=public_hash)
        
        file_instance.last_downloaded_at = timezone.now()
        file_instance.save(update_fields=['last_downloaded_at'])
        
        if not os.path.exists(file_instance.file.path):
            logger.error(f'Файл не найден на диске: {file_instance.file.path}')
            raise Http404('Файл не найден')
        
        logger.info(
            f'Файл скачан по публичной ссылке: {file_instance.display_name} '
            f'(UUID: {public_hash})'
        )

        view_mode = request.GET.get('view') == '1'
        can_view_inline = file_instance.mime_type in settings.VIEWABLE_MIME_TYPES
        as_attachment = not (view_mode and can_view_inline)
        
        response = FileResponse(
            open(file_instance.file.path, 'rb'),
            as_attachment=True,
            content_type=file_instance.mime_type
        )

        if as_attachment:
            response['Content-Disposition'] = f'attachment; filename="{file_instance.original_name}"'
        
        
        return response