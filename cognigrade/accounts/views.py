
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from cognigrade.utils.paginations import PagePagination

from .serializers import UserSerializer
from .models import User
from .utils import delete_user

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = PagePagination
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def get_queryset(self):
        qs = User.objects.all()
        if self.request.user.is_authenticated:
            if self.request.user.is_superadmin:
                return qs
            else :
                return qs.none()
        else:
            return qs.none()
    

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superadmin:
            user = self.get_object()
            if not user.is_deleted:
                delete_user(user, request)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError(
                {
                    "error": "User already deleted",
                    "code": "deleted"
                }
            )
        else:
            raise ValidationError(
                {
                    "error": "Permission required!",
                    "code": "permission-deny"
                }
            )


    @action(url_path='me', detail=False, methods=['GET'])
    def me(self, request, **kwargs):
        user = request.user
        return Response(UserSerializer(user).data)
    