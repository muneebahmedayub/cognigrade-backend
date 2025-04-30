
from rest_framework.routers import SimpleRouter

from .views import OMRViewSet, OMRSubmissionViewSet

omr_router = SimpleRouter()

omr_router.register(r'omr', OMRViewSet, basename='omr')
omr_router.register(r'omr-submission', OMRSubmissionViewSet, basename='omr-submission')