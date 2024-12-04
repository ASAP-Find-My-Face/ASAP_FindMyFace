import cv2
import numpy as np
from keras_facenet import FaceNet


import cv2
import numpy as np
from keras_facenet import FaceNet

def detect_face(image):
    """
    주어진 이미지에서 얼굴을 검출하고 FaceNet 모델 입력 크기로 조정합니다.
    image는 파일 경로(str) 또는 numpy 배열일 수 있습니다.
    """
    # 이미지가 numpy 배열인지 파일 경로인지 확인
    if isinstance(image, str):  # 파일 경로인 경우
        img = cv2.imread(image)
        if img is None:
            return None
    elif isinstance(image, np.ndarray):  # 이미 numpy 배열인 경우
        img = image
    else:
        raise ValueError("Input must be a file path or a numpy array.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return None

    (x, y, w, h) = faces[0]
    face = img[y:y+h, x:x+w]
    face_resized = cv2.resize(face, (160, 160))  # FaceNet 입력 크기로 조정

    return face_resized


def extract_features(face_image):
    """
    FaceNet을 사용하여 얼굴 이미지의 특징점을 추출합니다.
    """
    embedder = FaceNet()
    face = np.expand_dims(face_image, axis=0)
    embedding = embedder.embeddings(face)[0]
    return embedding
