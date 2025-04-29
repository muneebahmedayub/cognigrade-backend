
from rest_framework.routers import SimpleRouter

from .views import TheoryViewSet, TheorySubmissionViewSet

theory_router = SimpleRouter()

theory_router.register(r'theory', TheoryViewSet, basename='theory')
theory_router.register(r'submissions', TheorySubmissionViewSet, basename='theory-submission')