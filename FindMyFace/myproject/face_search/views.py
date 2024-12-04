import os
import random
import string
import pickle
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .models import FaceEncodingFile, VideoPlatformResult  # 모델 임포트
from django.views.decorators.csrf import csrf_exempt  # CSRF 비활성화 데코레이터
from io import BytesIO
from PIL import Image
import numpy as np  # NumPy 라이브러리 추가
import face_recognition  # facerecognition 라이브러리 추가

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
        random_key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        try:
            # 파일 처리
            for file in files:
                # 메모리 상에서 파일 처리
                image_stream = BytesIO(file.read())
                image = Image.open(image_stream).convert('RGB')  # RGB로 변환
                image_array = np.array(image)  # PIL 이미지를 NumPy 배열로 변환
                
                # 얼굴 검출 및 특징 추출
                face_locations = face_recognition.face_locations(image_array)  # 얼굴 위치 검출
                if face_locations:
                    print("Face detected successfully.")
                    face_encodings = face_recognition.face_encodings(image_array, face_locations)  # 얼굴 특징 추출
                    if face_encodings:
                        embeddings.append(face_encodings[0])  # 첫 번째 얼굴의 임베딩만 저장
                    else:
                        raise ValueError(f"Failed to extract features from {file.name}")
                else:
                    print(f"Face not detected in {file.name}")
                    raise ValueError(f"Face not detected in {file.name}")

            if len(embeddings) != 10:
                raise ValueError("Failed to process all images. Please ensure all images contain recognizable faces.")

            # 랜덤 키 생성
            output_path = os.path.join(settings.MEDIA_ROOT, 'face_encodings', f"{random_key}.pkl")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)  # face_encodings 디렉토리 생성
            print(f"Saving embeddings to pickle file: {output_path}")

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
