
from rest_framework.routers import SimpleRouter

from .views import InstitutionsViewSet

institutions_router = SimpleRouter()

institutions_router.register(r'institutions', InstitutionsViewSet, basename='institutions')