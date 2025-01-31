import os
import random
import string
import pickle
import hashlib  #해싱 모듈
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .models import FaceEncodingFile, VideoPlatformResult
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition

def generate_key_test_page(request):
    """
    테스트 키 생성 페이지를 렌더링합니다.
    """
    return render(request, 'test_generate_key.html')

@csrf_exempt
def create_face_key(request):
    """
    얼굴 이미지 키 생성 및 SQLite 저장
    """
    if request.method == 'POST':
        files = request.FILES.getlist('images')
        if len(files) < 10:
            return JsonResponse({"error": "At least 10 images are required."}, status=400)

        embeddings = []
        
        # 🔹 SHA-256 해싱을 사용한 12자리 키 생성
        user_email = request.POST.get('email', 'default@example.com')  # 사용자 이메일 받기 (없으면 기본값)
        raw_key = f"{user_email}{os.urandom(16).hex()}"  # 이메일 + 랜덤 16바이트 값 조합
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()[:12]  # SHA-256 해싱 후 앞 12자리 추출
        random_key = hashed_key  # 기존 random_key 변수 변경
        
        try:
            # 파일 처리
            for file in files:
                image_stream = BytesIO(file.read())
                image = Image.open(image_stream).convert('RGB')
                image_array = np.array(image)

                # 얼굴 검출 및 특징 추출
                face_locations = face_recognition.face_locations(image_array)
                if face_locations:
                    print("Face detected successfully.")
                    face_encodings = face_recognition.face_encodings(image_array, face_locations)
                    if face_encodings:
                        embeddings.append(face_encodings[0])
                    else:
                        raise ValueError(f"Failed to extract features from {file.name}")
                else:
                    print(f"Face not detected in {file.name}")
                    raise ValueError(f"Face not detected in {file.name}")

            if len(embeddings) != 10:
                raise ValueError("Failed to process all images. Please ensure all images contain recognizable faces.")

            # 🔹 해시 기반 키 값 적용하여 저장 경로 설정
            output_path = os.path.join(settings.MEDIA_ROOT, 'face_encodings', f"{random_key}.pkl")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 피클 파일 저장
            with open(output_path, 'wb') as f:
                pickle.dump(embeddings, f)

            return JsonResponse({
                "key": os.path.basename(output_path),
                "message": "Key successfully generated and saved."
            })

        except ValueError as e:
            print(f"ValueError: {e}")
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
