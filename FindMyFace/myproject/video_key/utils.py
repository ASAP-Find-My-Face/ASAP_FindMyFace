import os
import pickle
import cv2
import face_recognition
from django.conf import settings
from django.core.files.storage import default_storage
import time

def process_images_and_create_pickle(images):
    # 얼굴 특징 저장을 위한 딕셔너리
    face_encodings = {}

    # Media 경로 확인
    pickle_save_dir = os.path.join(settings.MEDIA_ROOT, 'key')
    if not os.path.exists(pickle_save_dir):
        os.makedirs(pickle_save_dir)

    # 이미지 처리
    for img_file in images:
        # 임시 저장
        temp_path = default_storage.save(f"temp/{img_file.name}", img_file)
        full_img_path = os.path.join(settings.MEDIA_ROOT, temp_path)

        # 이미지 읽기 및 얼굴 특징 추출
        image = cv2.imread(full_img_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_image)

        if encodings:
            face_encodings[img_file.name] = encodings[0]

        # 임시 파일 삭제
        os.remove(full_img_path)

    # 피클 파일 저장
    pickle_file_name = f"face_encodings_{int(time.time())}.pkl"
    pickle_file_path = os.path.join(pickle_save_dir, pickle_file_name)

    with open(pickle_file_path, 'wb') as f:
        pickle.dump(face_encodings, f)

    return pickle_file_path
