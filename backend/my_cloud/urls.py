from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import SPAView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/', include('users.urls')),  # ← должно быть именно так
    path('api/', include('files.urls')),

    re_path(r'^(?!api/|admin/|static/|media/).*$', SPAView.as_view(), name='spa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)