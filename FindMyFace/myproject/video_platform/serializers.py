from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    video_id = serializers.ReadOnlyField()  # video_id는 읽기 전용
    uploaded_at = serializers.ReadOnlyField()  # 업로드 시간 추가

    class Meta:
        model = Video
        fields = ['video_id', 'video_name', 'file_path', 'uploaded_at']