from django.contrib import admin
from myproject.face_search.models import FaceEncodingFile, VideoPlatformResult  # 올바른 경로로 수정

@admin.register(FaceEncodingFile)
class FaceEncodingFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'created_at')

@admin.register(VideoPlatformResult)
class VideoPlatformResultAdmin(admin.ModelAdmin):
    list_display = ('verification_code_id', 'created_at')