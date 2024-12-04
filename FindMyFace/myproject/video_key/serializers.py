from rest_framework import serializers
from .models import FaceKey, Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'uploaded_at']

class FaceKeySerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, write_only=True)

    class Meta:
        model = FaceKey
        fields = ['key', 'images', 'created_at']

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        face_key = FaceKey.objects.create(**validated_data)

        # 이미지 저장
        for image_data in images_data:
            Image.objects.create(face_key=face_key, **image_data)
        return face_key
