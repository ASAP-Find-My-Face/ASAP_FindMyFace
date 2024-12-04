from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from datetime import datetime
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, email, key=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, key=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, key=key, **extra_fields)

class CustomUser(AbstractBaseUser):
    custom_id = models.CharField(max_length=10, unique=True, primary_key=True, editable=False)  # PK로 설정
    email = models.EmailField(unique=True)
    key = models.CharField(max_length=16, editable=False, default='')  # 기본값 추가
    created_at = models.DateTimeField(auto_now_add=True)

    #is_active = models.BooleanField(default=True)
    #is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'User'

    def save(self, *args, **kwargs):
        if not self.custom_id:
            date_str = datetime.now().strftime('%m%d')
            users_today = CustomUser.objects.filter(
                created_at__date=datetime.now().date()
            ).count() + 1
            self.custom_id = f"{date_str}_{users_today}"

        if not self.key:  # key가 비어있는 경우에만 새로 생성
            self.key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        super().save(*args, **kwargs)
