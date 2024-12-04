import os
import json
import pickle
import cv2
import base64
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
from face_recognition import face_encodings, face_locations, face_distance

from .models import Video, VerificationCode
from .forms import VideoUploadForm
from .serializers import VideoSerializer

import logging
import subprocess

# 로깅 설정
logger = logging.getLogger(__name__)


# Match Videos HTML
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def match_videos_html(request):
    logger.info("match_videos_html called.")
    if request.method != 'POST':
        logger.error("Invalid request method.")
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Request data: {data}")

        key = data.get('key')
        if not key:
            logger.error("Key is missing in request.")
            return JsonResponse({"error": "Key is required."}, status=400)

        key_path = os.path.join(settings.MEDIA_ROOT, 'face_encodings', f"{key}.pkl")
        if not os.path.exists(key_path):
            logger.error(f"Key file not found at: {key_path}")
            return JsonResponse({"error": "Key file not found."}, status=404)

        with open(key_path, 'rb') as f:
            known_encodings = pickle.load(f)
            if not isinstance(known_encodings, list):
                logger.error("Invalid key file format.")
                return JsonResponse({"error": "Invalid key file format."}, status=500)

        videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        if not os.path.exists(videos_dir):
            logger.error("Videos directory not found.")
            return JsonResponse({"error": "Videos directory not found."}, status=404)

        video_files = [os.path.join(videos_dir, f) for f in os.listdir(videos_dir) if f.endswith('.mp4')]
        logger.info(f"Found video files: {video_files}")

        matched_videos = []
        for video_path in video_files:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.warning(f"Failed to open video file: {video_path}")
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

                    if not isinstance(frame_encodings, list) or len(frame_encodings) == 0:
                        logger.info("No face encodings found in the frame.")
                        continue

                    for face_encoding in frame_encodings:
                        distances = face_distance(np.array(known_encodings), face_encoding)
                        if len(distances) == 0:
                            logger.warning("Distances calculation failed.")
                            continue

                        best_match_index = np.argmin(distances)
                        best_distance = distances[best_match_index]

                        if best_distance < 0.35:
                            match_time = frame_count / fps
                            frame_image_path = os.path.join(
                                settings.MEDIA_ROOT, 
                                'matched_frames', 
                                f"{os.path.basename(video_path)}_frame_{frame_count}.jpg"
                            )
                            os.makedirs(os.path.dirname(frame_image_path), exist_ok=True)
                            cv2.imwrite(frame_image_path, frame)

                            matched_videos.append({
                                "video_name": os.path.basename(video_path),
                                "first_match_time": float(match_time),
                                "match_similarity": float(best_distance),
                                "frame_image_url": f"/media/matched_frames/{os.path.basename(frame_image_path)}"
                            })
                            matched = True
                            break

                if matched:
                    break

                frame_count += 1
            cap.release()

        logger.info("Matching process completed successfully.")
        return JsonResponse({"matched_videos": matched_videos}, status=200)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({"error": "Invalid JSON input."}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

# Get Verification Code
@api_view(['GET'])
def get_verification_code(request, input_code):
    verification = get_object_or_404(VerificationCode, verification_code=input_code)
    return Response({
        'user_id': verification.user.id,
        'verification_code': verification.verification_code
    }, status=200)


# Match Form HTML
def match_form_html(request):
    return render(request, 'match_form.html')


# Upload Video
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_name = form.cleaned_data['video_name']
            video_file = form.cleaned_data['video_file']

            video = Video.objects.create(
                video_name=video_name,
                file_path=video_file
            )
            path = default_storage.save(video.file_path.name, ContentFile(video_file.read()))
            return render(request, 'upload_success.html', {'video': video})
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})


# REST API for Video Upload
class VideoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('file')
        video_name = request.data.get('video_name')

        if not video_file or not video_name:
            return Response({"error": "Both video file and video name are required."}, status=status.HTTP_400_BAD_REQUEST)

        video_instance = Video(video_name=video_name, file_path=video_file.name)
        video_instance.save()

        video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        serializer = VideoSerializer(video_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# REST API for Video List
class VideoListView(APIView):
    def get(self, request, *args, **kwargs):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)
        for video in serializer.data:
            video['file_path'] = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, video['file_path']))
        return Response(serializer.data, status=status.HTTP_200_OK)


# Process Video View
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

