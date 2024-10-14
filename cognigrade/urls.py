"""
URL configuration for cognigrade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from cognigrade.accounts.urls import users_router
from cognigrade.institutions.urls import institutions_router


router = DefaultRouter()
router.registry.extend(users_router.registry)
router.registry.extend(institutions_router.registry)

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/v1/', include(router.urls)),
    path(r'api/v1/login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(r'api/v1/login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(r'api/v1/login/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
