
from rest_framework.routers import SimpleRouter

from .views import TheoryViewSet

theory_router = SimpleRouter()

theory_router.register(r'theory', TheoryViewSet, basename='theory')