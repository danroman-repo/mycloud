from django.urls import path
from .views import (
    FileListView,
    FileUploadView,
    FileDetailView,
    FileRenameView,
    FileDownloadView,
    FileShareView,
    PublicFileDownloadView,
)

urlpatterns = [
    path('files/', FileListView.as_view(), name='file-list'),
    
    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    
    path('files/<int:pk>/', FileDetailView.as_view(), name='file-detail'),
    
    path('files/<int:pk>/rename/', FileRenameView.as_view(), name='file-rename'),
    
    path('files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    
    path('files/<int:pk>/share/', FileShareView.as_view(), name='file-share'),
    
    path('public/files/<uuid:public_hash>/download/', PublicFileDownloadView.as_view(), name='public-file-download'),
]