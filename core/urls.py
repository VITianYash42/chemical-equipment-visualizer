from django.urls import path
# The error happened because DownloadPDFView was missing from this line:
from .views import FileUploadView, HistoryView, DownloadPDFView 

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:file_id>/', DownloadPDFView.as_view(), name='download-pdf'),
]