from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OMR
from .serializer import OMRSerializer
from cognigrade.utils.paginations import PagePagination
from cognigrade.utils.process_omr import process_omr
from rest_framework.response import Response
from rest_framework import status
import os
from django.conf import settings
import random
from rest_framework.decorators import action

# Create your views here.
class OMRViewSet(viewsets.ModelViewSet):
    queryset = OMR.objects.all()
    serializer_class = OMRSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PagePagination
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return OMR.objects.filter(classroom__teacher=user)
        elif user.role == 'student':
            return OMR.objects.filter(classroom__enrollments__student=user)
        elif user.role == 'admin':
            return OMR.objects.filter(classroom__course__institution=user.institution)
        elif user.role == 'superadmin':
            return OMR.objects.all()
        return OMR.objects.none()
    
    @action(url_path='process', detail=True, methods=['POST'])
    def process_omr(self, request, pk=None):
        omr = self.get_object()
        image_file = request.FILES.get('image')
        
        if not image_file:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        correct_answers = [chr(64 + answer) for answer in omr.questions.values_list('answer', flat=True)]
        
        image_path = os.path.join(settings.MEDIA_ROOT, 'omr', f"{image_file.name}_{random.randint(1, 1000000)}.jpg")
        with open(image_path, 'wb') as f:
            f.write(image_file.read())
        score, answers = process_omr(image_path, correct_answers)
        return Response({'score': score, 'answers': answers}, status=status.HTTP_200_OK)
