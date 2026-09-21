import uuid
from django.db import models
from django.conf import settings


def user_directory_path(instance, filename):
    """
    Формируем путь: media/user_<id>/<uuid>_<расширение>
    Это гарантирует отсутствие конфликтов имён.
    """
    import os
    ext = os.path.splitext(filename)[1]
    unique_name = f'{uuid.uuid4()}{ext}'
    return f'user_{instance.owner_id}/{unique_name}'


class File(models.Model):
    """Файл в облачном хранилище пользователя."""
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Владелец'
    )
    original_name = models.CharField(
        max_length=255,
        verbose_name='Оригинальное имя файла'
    )
    display_name = models.CharField(
        max_length=255,
        verbose_name='Отображаемое имя (можно переименовывать)'
    )
    comment = models.TextField(
        blank=True,
        default='',
        verbose_name='Комментарий'
    )
    size = models.BigIntegerField(
        verbose_name='Размер (байт)'
    )
    file = models.FileField(
        upload_to=user_directory_path,
        verbose_name='Файл на диске'
    )
    public_hash = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Публичная ссылка (UUID)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Последнее скачивание'
    )
    
    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.display_name} ({self.owner.username})'
    
    @property
    def public_url(self):
        """Формируем обезличенную публичную ссылку."""
        return f'/api/public/files/{self.public_hash}/download/'