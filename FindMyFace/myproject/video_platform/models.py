from django.db import models
from django.conf import settings
import uuid

# Video 모델
class Video(models.Model):
    video_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID로 고유 ID 생성
    video_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='videos/')  # 파일 업로드 경로만 사용
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 업로드 시간 추가
    description = models.TextField(blank=True)

    def __str__(self):
        return self.video_name
    
    class Meta:
        app_label = 'video_platform'  # 앱 이름 명시

# VerificationCode 모델
class VerificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 사용자와 연결
    verification_code = models.CharField(max_length=255, unique=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='verification_codes', null=True, blank=True)

    def __str__(self):
        return f"Verification Code: {self.verification_code}"

# Search 모델
class Search(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field="custom_id",  # CustomUser 모델의 기본 키(custom_id)를 참조
        on_delete=models.CASCADE
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE)  # 검색된 동영상
    search_date = models.DateTimeField(auto_now_add=True)  # 검색한 날짜와 시간 기록

    def __str__(self):
        return f"{self.user.custom_id} searched for {self.video.video_name} on {self.search_date}"

# Result 모델
class Result(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)  # 비디오와 연결
    verification_code = models.ForeignKey(VerificationCode, on_delete=models.CASCADE, null=True, blank=True)  # 검증 코드와 연결 (선택적)
    result_data = models.TextField()  # 결과 데이터를 저장할 필드
    created_at = models.DateTimeField(auto_now_add=True)  # 결과 생성 날짜

    def __str__(self):
        return f"Result for {self.video.video_name} at {self.created_at}"

