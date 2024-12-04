"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from myproject.accounts.views import register_page, UserViewSet
from . import views
from .views import video_list
from django.views.generic import TemplateView
from myproject.video_platform.views import upload_video

user_lookup = UserViewSet.as_view({
    'get': 'retrieve_key'
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('face_search/', include('myproject.face_search.urls')),  # face_search 앱 URL 연결
    
    # 프런트용
    path('', views.video_list, name='home'),  # 영상 리스트
    path('video/<str:video_name>/', views.video_detail, name='video_detail'),  # 세부 페이지
    path('first-fmf/', TemplateView.as_view(template_name='first_fmf.html'), name='first-fmf'),  # 첫 페이지
    path('find-my-face/', views.find_my_face, name='find-my-face'),  # FIND MY FACE
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    
    # 회원가입 페이지
    path('accounts/register/', register_page, name='register-page'),
    path('accounts/register-api', UserViewSet.as_view({'post': 'create'}), name='user-register'),  # 회원가입 API
    path('accounts/lookup/', user_lookup, name='user-lookup'),
    
    # 회원 조회 페이지: 존재하지 않는 이메일일 경우 회원가입 페이지로 리다이렉트
    path('accounts/lookup/', user_lookup, name='user-lookup'),
    
    # video_platform 앱의 URL 연결
    path('video_platform/', include('myproject.video_platform.urls')),  # video_platform 관련 API
    
    # HTML 렌더링용 video upload URL 추가
    path('video_platform/upload/', upload_video, name='upload-video-html'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
