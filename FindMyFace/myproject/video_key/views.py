from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from .utils import process_images_and_create_pickle  # 유틸리티 함수 사용

def upload_images(request):
    if request.method == "POST":
        images = request.FILES.getlist('images')  # 업로드된 이미지 리스트
        if len(images) == 0:
            return render(request, 'input_image.html', {"error": "Please upload at least one image."})
        
        if len(images) > 10:
            return render(request, 'input_image.html', {"error": "You can upload up to 10 images at a time."})
        
        try:
            # 이미지 처리 및 피클 파일 생성
            pickle_file_path = process_images_and_create_pickle(images)
            success_message = f"Processing completed. File saved at {pickle_file_path}"
            return render(request, 'input_image.html', {"success": success_message})
        except Exception as e:
            return render(request, 'input_image.html', {"error": f"An error occurred: {str(e)}"})
    
    return render(request, 'input_image.html')
