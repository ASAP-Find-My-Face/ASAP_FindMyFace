from django import forms

class VideoUploadForm(forms.Form):
    video_name = forms.CharField(max_length=255)
    video_file = forms.FileField()

# video_platform/views.py
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from .models import Video

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_name = form.cleaned_data['video_name']
            video_file = form.cleaned_data['video_file']

            # Video 모델 인스턴스 생성 및 저장
            video = Video.objects.create(
                video_name=video_name,
                file=video_file  # FileField로 파일 저장
            )
            return render(request, 'upload_success.html', {'video': video})
    else:
        form = VideoUploadForm()

    return render(request, 'upload_video.html', {'form': form})