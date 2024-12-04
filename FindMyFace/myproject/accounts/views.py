from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from django.http import JsonResponse
from .models import CustomUser
from django.shortcuts import render, redirect

# 일반 Django 뷰 함수로 작성
def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # 이메일 중복 체크
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': '동일한 이메일이 이미 존재합니다.'}, status=400)

        # 사용자 생성
        user = CustomUser.objects.create(email=email)
        user.save()

        # 회원가입 완료 후 리디렉션
        return redirect('/face_search/generate_key_test/')  # 성공 시 리디렉션

    return render(request, 'register.html')

class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # 회원가입
    def create(self, request):
        email = request.data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': '동일한 이메일이 이미 존재합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'custom_id': user.custom_id,  # custom_id를 반환
                'email': user.email,
                'key': user.key  # key 값을 그대로 반환
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 회원 조회
    def retrieve(self, request, pk=None):
        try:
            user = CustomUser.objects.get(custom_id=pk)  # custom_id로 조회
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    # 회원 key 조회
    def retrieve_key(self, request):
        custom_id = request.query_params.get('custom_id')  # custom_id로 검색
        if not custom_id:
            return Response({'error': 'custom_id를 제공해야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(custom_id=custom_id)
            return Response({'key': user.key}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
