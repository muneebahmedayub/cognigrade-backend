
from rest_framework.routers import SimpleRouter

from .views import OMRViewSet

omr_router = SimpleRouter()

omr_router.register(r'omr', OMRViewSet, basename='omr')