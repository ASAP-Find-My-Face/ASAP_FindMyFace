import os
import cv2
import pickle
import random
import string
from face_recognition import face_encodings
from django.conf import settings

def handle_uploaded_video(video_path):
    """Handle the uploaded video, detect faces, save each frame with faces to a separate file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Video cannot be opened.")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 프레임별로 얼굴 인코딩
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_encodings(rgb_frame)

        if encodings:
            # 얼굴이 인식된 프레임의 파일 이름 정의
            video_name = os.path.basename(video_path).split('.')[0]
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            encodings_file_name = f"{video_name}_frame{frame_count}_{random_suffix}.pkl"
            encodings_file_path = os.path.join(settings.MEDIA_ROOT, 'face_encodings', encodings_file_name)
            
            # 인코딩 데이터를 바이너리 파일로 저장
            with open(encodings_file_path, 'wb') as f:
                pickle.dump(encodings, f)

        frame_count += 1

    cap.release()

# 업로드된 영상 처리 후 결과 반환 함수
def upload_and_process_video(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file']
        video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
        
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        # 영상 처리 및 얼굴 인코딩 데이터 저장
        try:
            handle_uploaded_video(video_path)
            return JsonResponse({'message': 'Video processed successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method or no video file provided'}, status=400)
