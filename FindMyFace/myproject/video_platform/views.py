import os
import json
import pickle
import logging
import cv2
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from face_recognition import face_encodings, face_locations, face_distance
from django.shortcuts import render, redirect
from .models import Video, VerificationCode
from .forms import VideoUploadForm
from .serializers import VideoSerializer

# Process Video View
import subprocess

logger = logging.getLogger(__name__)

#SHA-256 해시 키 생성 함수
def generate_hash_key(data):
    """
    입력 데이터를 기반으로 SHA-256 해시를 생성하고 12자리만 반환하는 함수.
    """
    hash_object = hashlib.sha256(data.encode())
    return hash_object.hexdigest()[:12]  # 12자리만 사용

#동영상에서 얼굴 특징점 추출
def extract_face_features(video_path):
    """
    동영상에서 얼굴 특징점을 추출하여 반환하는 함수.
    """
    cap = cv2.VideoCapture(video_path)
    face_embeddings = []

    if not cap.isOpened():
        return None

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = max(fps // 2, 1)  # 초당 2프레임씩 추출
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations_list = face_locations(rgb_frame)

            if face_locations_list:
                face_enc = face_encodings(rgb_frame, face_locations_list)
                if face_enc and len(face_enc) > 0:  # 추가된 예외 처리
                    face_embeddings.append(face_enc[0])  # 첫 번째 얼굴 특징점만 저장

        frame_count += 1

    cap.release()
    return face_embeddings if face_embeddings else None


def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_name = form.cleaned_data['video_name']
            video_file = form.cleaned_data['video_file']

            # 파일 저장
            file_path = default_storage.save(f"videos/{video_file.name}", ContentFile(video_file.read()))

            # Video 모델에 저장
            video = Video.objects.create(video_name=video_name, file_path=file_path)

            # 업로드 성공 페이지로 이동
            return render(request, 'upload_success.html', {'video': video})

        else:
            return render(request, 'upload_video.html', {'form': form, 'error_message': "Invalid form submission."})

    else:
        form = VideoUploadForm()
        return render(request, 'upload_video.html', {'form': form})


#REST API 비디오 업로드 (DRF 기반)
class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('file')
        video_name = request.data.get('video_name')

        if not video_file or not video_name:
            return Response({"error": "Both video file and video name are required."}, status=status.HTTP_400_BAD_REQUEST)

        video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_file.name)
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        try:
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            logger.info(f"비디오 저장 완료: {video_path}")
        except Exception as e:
            logger.error(f"파일 저장 실패: {e}")
            return Response({"success": False, "error": "파일 저장 실패"}, status=500)

        video_instance = Video.objects.create(video_name=video_name, file_path=video_file.name)
        logger.info(f"DB 저장 완료: {video_name}")

        serializer = VideoSerializer(video_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# REST API 비디오 목록 조회
class VideoListView(APIView):
    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)

        for video in serializer.data:
            video['file_path'] = request.build_absolute_uri(settings.MEDIA_URL + video['file_path'])

        return Response(serializer.data, status=status.HTTP_200_OK)

#얼굴 데이터 & 비디오 매칭
def match_videos_html(request):
    logger.info("match_videos_html called.")
    if request.method != 'POST':
        logger.error("Invalid request method.")
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        key = data.get('key')

        if not key:
            return JsonResponse({"error": "Key is required."}, status=400)

        key_path = os.path.join(settings.MEDIA_ROOT, 'face_encodings', f"{key}.pkl")
        if not os.path.exists(key_path):
            return JsonResponse({"error": "Key file not found."}, status=404)

        with open(key_path, 'rb') as f:
            known_encodings = pickle.load(f)

        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        video_files = [os.path.join(videos_dir, f) for f in os.listdir(videos_dir) if f.endswith('.mp4')]

        matched_videos = []
        for video_path in video_files:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                continue

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_interval = max(fps // 2, 1)
            frame_count = 0
            matched = False

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_encodings = face_encodings(rgb_frame)

                    for face_encoding in frame_encodings:
                        distances = face_distance(np.array(known_encodings), face_encoding)

                        if np.min(distances) < 0.35:
                            matched = True
                            break

                if matched:
                    break
                frame_count += 1
            cap.release()

        return JsonResponse({"matched_videos": matched_videos}, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

#GET Verification Code
@api_view(['GET'])
def get_verification_code(request, input_code):
    verification = get_object_or_404(VerificationCode, verification_code=input_code)
    return Response({"user_id": verification.user.id, "verification_code": verification.verification_code}, status=200)

#Match Form HTML
def match_form_html(request):
    return render(request, 'match_form.html')



def process_video_view(request):
    if request.method == 'POST':
        try:
            video_dir = os.path.join(settings.MEDIA_ROOT, "videos")
            script_path = os.path.join(settings.BASE_DIR, "video_processing.py")
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                cwd=video_dir
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            return JsonResponse({"result": output}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Error processing video: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)
