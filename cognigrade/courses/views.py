from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Course, Classroom
from .serializers import CourseSerializer, ClassroomSerializer
from .filters import CourseFilter, ClassroomFilter
from cognigrade.utils.paginations import PagePagination


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_class = CourseFilter
    pagination_class = PagePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        elif user.is_admin:
            return super().get_queryset().filter(institution=user.institution)
        elif user.is_teacher:
            return super().get_queryset().filter(classrooms__teacher=user).distinct()
        elif user.is_student:
            return super().get_queryset().filter(classrooms__enrollments__student=user).distinct()
        
    
class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filter_class = ClassroomFilter
    pagination_class = PagePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        elif user.is_admin:
            return super().get_queryset().filter(course__institution=user.institution)
        elif user.is_teacher:
            return super().get_queryset().filter(teacher=user)
        elif user.is_student:
            return super().get_queryset().filter(enrollments__student=user)
        else:
            return super().get_queryset().none()
    

# class EnrollmentViewSet(viewsets.ModelViewSet):
#     queryset = Enrollment.objects.all()
#     serializer_class = EnrollmentSerializer
#     filter_class = EnrollmentFilter
#     pagination_class = PagePagination
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser:
#             return super().get_queryset()
#         elif user.is_admin:
#             return super().get_queryset().filter(classroom__course__institution=user.institution)
#         elif user.is_teacher:
#             return super().get_queryset().filter(classroom__teacher=user)
#         elif user.is_student:
#             return super().get_queryset().filter(student=user)
#         else:
#             return super().get_queryset().none()