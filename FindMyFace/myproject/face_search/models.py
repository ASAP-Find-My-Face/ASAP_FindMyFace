from django.conf import settings
from django.db import models

class FaceEncodingFile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="face_encoding_files",
        null=True,  # NULL 값 허용
        blank=True  # Django Admin 및 폼에서 빈 값 허용
    )
    file = models.FileField(upload_to="face_encodings/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.file.name}"


class VideoPlatformResult(models.Model):
    verification_code_id = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.verification_code_id


# from django.conf import settings
# from django.db import models

# class FaceEncodingFile(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # 기존 auth.User 대신 settings.AUTH_USER_MODEL 사용
#         on_delete=models.CASCADE,
#         related_name="face_encoding_files"
#     )
#     file = models.FileField(upload_to="face_encodings/")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.file.name}"

# class VideoPlatformResult(models.Model):
#     verification_code_id = models.CharField(max_length=8, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.verification_code_id
