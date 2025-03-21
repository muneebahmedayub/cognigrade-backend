from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Theory
from .serializer import TheorySerializer
from cognigrade.utils.paginations import PagePagination
from .filters import TheoryFilter

# Create your views here.
class TheoryViewSet(viewsets.ModelViewSet):
    queryset = Theory.objects.all()
    serializer_class = TheorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PagePagination
    filterset_class = TheoryFilter
    
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'teacher':
            return qs.filter(classroom__teacher=user)
        elif user.role == 'student':
            return qs.filter(classroom__enrollments__student=user)
        elif user.role == 'admin':
            return qs.filter(classroom__course__institution=user.institution)
        elif user.role == 'superadmin':
            return qs.all()
        return qs.none()
    