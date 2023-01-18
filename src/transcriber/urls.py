from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('start-file-upload/', views.audio_file_upload_start_view, name='start_file_upload'),
    path('finish-file-upload/', views.audio_file_upload_finish_view, name='finish_file_upload'),
    path('start-file-transcription/', views.transcribe_audio_file_view, name='start_file_transcription')
]
