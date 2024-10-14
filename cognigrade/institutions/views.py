from rest_framework.viewsets import ModelViewSet
from .serializers import InstitutionsSerializers
from .models import Institutions
from rest_framework import permissions, status
from cognigrade.utils.paginations import PagePagination
from cognigrade.accounts.permissions import IsSuperAdminUser, IsAdminUser


class InstitutionsViewSet(ModelViewSet):
    serializer_class = InstitutionsSerializers
    pagination_class = PagePagination
    permission_classes = []

    def initial(self, request, *args, **kwargs):
        if self.permission_classes and len(self.permission_classes):
            pass
        elif request.method in permissions.SAFE_METHODS:
            self.permission_classes = (permissions.AllowAny,)
        else:
            self.permission_classes = (IsSuperAdminUser, IsAdminUser,)
        return super(InstitutionsViewSet, self).initial(request, *args, **kwargs)

    def get_queryset(self):
        qs = Institutions.objects.all()
        if self.request.user.is_authenticated:
            if self.request.user.is_superadmin:
                return qs
            # elif self.request.user.is_admin:
            #     return qs.filter(institution_user=self.request.user)
            else:
                return qs.filter(institution_user=self.request.user)
        else:
            return qs.none()