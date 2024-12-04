from django.urls import path
from . import views

app_name = 'face_key'

urlpatterns = [
    path('upload/', views.upload_images, name='upload_images'),
]
