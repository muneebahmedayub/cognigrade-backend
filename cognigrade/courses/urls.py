
from rest_framework.routers import SimpleRouter

from .views import CourseViewSet, ClassroomViewSet

courses_router = SimpleRouter()

courses_router.register(r'courses', CourseViewSet, basename='courses')
courses_router.register(r'classrooms', ClassroomViewSet, basename='classrooms')