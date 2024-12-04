from django.shortcuts import render, redirect
from django.shortcuts import render
from django.conf import settings
import os
from django.shortcuts import render, get_object_or_404
from myproject.video_platform.models import Video  # Video 모델을 사용한다고 가정

def video_list(request):
    video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    videos = []
    for file_name in os.listdir(video_dir):
        if file_name.endswith(('.mp4', '.avi', '.mkv')):  # 지원하는 파일 형식
            videos.append({
                'video_name': file_name,
                'file_path': os.path.join(settings.MEDIA_URL, 'videos', file_name),
            })
    return render(request, 'home.html', {'videos': videos})





def video_detail(request, video_name):
    # media/videos 디렉토리에서 해당 파일 찾기
    video_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    video_path = os.path.join(video_dir, video_name)
    
    # 파일이 존재하지 않을 경우 404 페이지 반환
    if not os.path.exists(video_path):
        from django.http import Http404
        raise Http404("Video does not exist")

    # 브라우저에서 접근 가능한 경로를 생성
    video_url = os.path.join(settings.MEDIA_URL, 'videos', video_name)

    return render(request, 'video_detail.html', {
        'video_name': video_name,
        'video_url': video_url,
    })



def home(request):
    return render(request, 'home.html')

def find_my_face(request):
    return render(request, 'find_my_face.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def upload(request):
    return render(request, 'upload.html')


def register_page(request):
    if request.method == "POST":
        email = request.POST.get("email")  # 사용자가 입력한 이메일 가져오기
        # 회원가입 처리 로직 (예: 데이터베이스 저장 등)
        print(f"User registered with email: {email}")

        # 회원가입 처리 후 리디렉션
        return redirect('/face_search/generate_key_test/')  # 리디렉션 URL 명시
    
    # GET 요청일 경우 회원가입 페이지 렌더링
    return render(request, 'register.html')
