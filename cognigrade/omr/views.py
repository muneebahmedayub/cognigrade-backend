from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OMR
from .serializer import OMRSerializer

# Create your views here.
class OMRViewSet(viewsets.ModelViewSet):
    queryset = OMR.objects.all()
    serializer_class = OMRSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return OMR.objects.filter(teacher=user)
        elif user.role == 'student':
            return OMR.objects.filter(classroom__enrollments__student=user)
        elif user.role == 'admin':
            return OMR.objects.filter(classroom__course__institution=user.institution)
        return OMR.objects.none()
    