from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

from .views import (
    match_form_html,
    match_videos_html,
    upload_video,
    VideoUploadView,
    VideoListView,
    get_verification_code,
    process_video_view,
)

urlpatterns = [
    path('match/form/', match_form_html, name='match-form'),
    path('match/json/', match_videos_html, name='match-videos'),
    path('upload/', upload_video, name='upload-video'),
    path('upload/api/', VideoUploadView.as_view(), name='video-upload-api'),
    path('list/', VideoListView.as_view(), name='video-list'),
    path('verify/<str:input_code>/', get_verification_code, name='get-verification-code'),
    path('process-video/', process_video_view, name='process-video'),
]