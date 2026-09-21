import re
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import EmailValidator

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password', 'password_confirm')
    
    def validate_username(self, value):
        """Валидация логина: латиница + цифры, первая буква, 4-20 символов."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]{3,19}$', value):
            raise serializers.ValidationError(
                'Логин должен содержать 4-20 символов, начинаться с буквы, '
                'только латинские буквы и цифры.'
            )
        return value
    
    def validate_email(self, value):
        """Валидация email."""
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError('Некорректный формат email.')
        return value
    
    def validate_password(self, value):
        """Валидация пароля: минимум 6 символов, заглавная буква, цифра, спецсимвол."""
        if len(value) < 6:
            raise serializers.ValidationError('Пароль должен содержать минимум 6 символов.')
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                'Пароль должен содержать хотя бы одну заглавную букву (A-Z).'
            )
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну цифру.')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
            raise serializers.ValidationError(
                'Пароль должен содержать хотя бы один специальный символ.'
            )
        
        return value
    
    def validate(self, data):
        """Проверка совпадения паролей."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Пароли не совпадают.'
            })
        return data
    
    def create(self, validated_data):
        """Создание пользователя."""
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            is_admin=False
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа в систему."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Проверка учетных данных."""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Неверный логин или пароль.')
            
            if not user.is_active:
                raise serializers.ValidationError('Пользователь деактивирован.')
        else:
            raise serializers.ValidationError('Необходимо указать логин и пароль.')
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных пользователя."""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email', 'is_admin', 'storage_path', 'created_at')
        read_only_fields = ('id', 'storage_path', 'created_at')


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка пользователей (админ-панель)."""
    
    files_count = serializers.SerializerMethodField()
    files_total_size = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email', 'is_admin', 'storage_path', 
                  'created_at', 'files_count', 'files_total_size')
        read_only_fields = ('id', 'storage_path', 'created_at')
    
    def get_files_count(self, obj):
        """Количество файлов пользователя."""
        return obj.files.count()
    
    def get_files_total_size(self, obj):
        """Общий размер файлов пользователя."""
        from django.db.models import Sum
        result = obj.files.aggregate(total_size=Sum('size'))
        return result['total_size'] or 0