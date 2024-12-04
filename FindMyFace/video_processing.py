import cv2
import os
import numpy as np
from django.conf import settings

# 경로 설정
project_root = os.getcwd()  # 현재 프로젝트 루트 디렉토리
video_directory = os.path.join(settings.MEDIA_ROOT, "videos")  # 동영상 파일이 있는 디렉토리
output_directory = os.path.join(settings.MEDIA_ROOT, "output")  # 매칭 결과를 저장할 디렉토리

# 디렉토리가 없으면 생성
if not os.path.exists(video_directory):
    os.makedirs(video_directory)  # 동영상 디렉토리 생성
    print(f"Created missing directory: {video_directory}")

if not os.path.exists(output_directory):
    os.makedirs(output_directory)  # 출력 디렉토리 생성
    print(f"Created missing directory: {output_directory}")
    
# 얼굴 인식 모델 (예: Haarcascade 사용)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# 매칭 임계값 설정
MATCH_THRESHOLD = 0.5  # 매칭 성공 기준 (0.4 ~ 0.6 사이 값 추천)

# 동영상 목록 가져오기
video_files = [f for f in os.listdir(video_directory) if f.endswith(('.mp4', '.avi', '.mov'))]

if not video_files:
    print("처리할 동영상이 없습니다!")
    exit()

# 결과 저장 폴더 생성
os.makedirs(output_directory, exist_ok=True)

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"동영상을 열 수 없습니다: {video_path}")
        return

    print(f"처리 중: {video_path}")
    matched = False
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 얼굴 감지
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_roi = gray_frame[y:y+h, x:x+w]  # 얼굴 영역

                # 매칭율 계산 (임의로 임계값 기준 적용)
                match_score = np.random.uniform(0.4, 0.9)  # 여기선 임의의 매칭율 사용
                if match_score > MATCH_THRESHOLD:
                    # 매칭 성공 시 정보 출력
                    matched = True
                    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)  # 초 단위로 계산

                    # 매칭된 이미지 저장
                    matched_image_path = os.path.join(output_directory, f"match_{os.path.basename(video_path)}_frame{frame_count}.jpg")
                    cv2.imwrite(matched_image_path, frame)

                    print(f"매칭 성공! 파일: {video_path}")
                    print(f"매칭된 프레임 시간: {timestamp}초")
                    print(f"매칭율: {match_score:.2f}")
                    print(f"저장된 매칭 이미지: {matched_image_path}")

                    # 매칭 결과 출력 후 비디오 정지
                    break

        if matched:
            break

    cap.release()

# 모든 동영상 처리
for video_file in video_files:
    video_path = os.path.join(video_directory, video_file)
    process_video(video_path)

print("모든 동영상 처리가 완료되었습니다!")
