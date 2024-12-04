from django.urls import path
from .views import generate_key_test_page, create_face_key

urlpatterns = [
    path('generate_key_test/', generate_key_test_page, name='generate-key-test'),
    path('create-face-key/', create_face_key, name='create-face-key'),
]
