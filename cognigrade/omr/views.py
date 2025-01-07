from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OMR
from .serializer import OMRSerializer
from cognigrade.utils.paginations import PagePagination

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
    