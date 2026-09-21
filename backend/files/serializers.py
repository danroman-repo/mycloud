from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о файле."""
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    public_url = serializers.SerializerMethodField()
    size_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = (
            'id', 'owner', 'owner_username', 'original_name', 'display_name',
            'comment', 'size', 'size_formatted', 'uploaded_at', 'last_downloaded_at',
            'public_hash', 'public_url'
        )
        read_only_fields = ('id', 'owner', 'original_name', 'size', 'uploaded_at', 
                           'last_downloaded_at', 'public_hash')
    
    def get_public_url(self, obj):
        """Формируем полную публичную ссылку."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.public_url)
        return obj.public_url
    
    def get_size_formatted(self, obj):
        """Форматируем размер файла."""
        size = obj.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"


class FileUploadSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки файла."""
    
    file = serializers.FileField()
    
    class Meta:
        model = File
        fields = ('file', 'comment')
    
    def create(self, validated_data):
        """Создание файла."""
        uploaded_file = validated_data['file']
        
        file_instance = File.objects.create(
            owner=self.context['request'].user,
            original_name=uploaded_file.name,
            display_name=uploaded_file.name,
            size=uploaded_file.size,
            file=uploaded_file,
            comment=validated_data.get('comment', '')
        )
        
        return file_instance


class FileRenameSerializer(serializers.Serializer):
    """Сериализатор для переименования файла."""
    
    display_name = serializers.CharField(max_length=255)
    
    def validate_display_name(self, value):
        """Валидация нового имени."""
        if not value.strip():
            raise serializers.ValidationError('Имя файла не может быть пустым.')
        return value.strip()


class FileCommentSerializer(serializers.Serializer):
    """Сериализатор для изменения комментария."""
    
    comment = serializers.CharField(allow_blank=True, required=False, default='')