import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Кастомная модель пользователя."""
    
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z][a-zA-Z0-9]{3,19}$',
        message='Логин: 4-20 символов, начинается с буквы, только латиница и цифры.'
    )
    
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[username_validator],
        help_text='Логин: первая буква, далее буквы/цифры, 4-20 символов',
        error_messages={
            'unique': 'Пользователь с таким логином уже существует.',
        }
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name='Полное имя'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        error_messages={
            'unique': 'Пользователь с таким email уже существует.',
        }
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name='Признак администратора',
        help_text='Доступ к админ-интерфейсу и чужим хранилищам'
    )
    storage_path = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        verbose_name='Путь к хранилищу'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username} ({self.full_name})'
    
    def save(self, *args, **kwargs):
        if not self.storage_path and self.pk:
            self.storage_path = f'user_{self.pk}'
        super().save(*args, **kwargs)