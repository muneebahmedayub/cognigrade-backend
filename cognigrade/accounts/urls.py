
from rest_framework.routers import SimpleRouter

from .views import UserViewSet

users_router = SimpleRouter()

users_router.register(r'users', UserViewSet, basename='users')