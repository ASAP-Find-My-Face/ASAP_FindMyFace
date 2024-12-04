from django.contrib import admin
from .models import Video, VerificationCode, Search, Result

admin.site.register(Video)
admin.site.register(VerificationCode)
admin.site.register(Search)
admin.site.register(Result)
