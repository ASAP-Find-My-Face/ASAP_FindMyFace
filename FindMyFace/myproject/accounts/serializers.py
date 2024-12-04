from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    key = serializers.CharField(read_only=True)  # key를 읽기 전용 필드로 설정

    class Meta:
        model = CustomUser
        fields = ['custom_id', 'email', 'key']  # id를 제외하고 custom_id를 PK로 사용
        read_only_fields = ['custom_id', 'key']  # custom_id와 key는 읽기 전용

    def create(self, validated_data):
        email = validated_data['email']
        user = CustomUser(email=email)
        user.save()  # 여기서 custom_id와 key가 자동 생성됨
        return user
