from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from cognigrade.utils.paginations import PagePagination

from .serializers import UserSerializer
from .models import User
from .utils import delete_user
from .permissions import IsSuperAdminUser, IsAdminUser
from .filters import UserFilter
class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = PagePagination
    permission_classes = []
    queryset = User.objects.all()
    filterset_class = UserFilter

    def get_queryset(self):
        qs = User.objects.all()
        if self.request.user.is_authenticated:
            if self.request.user.is_superadmin:
                return qs
            elif self.request.user.is_admin:
                return qs.filter(institution=self.request.user.institution)
            elif self.request.user.is_teacher:
                return qs.filter(classrooms__in=self.request.user.assigned_classrooms.all())
            else:
                return qs.filter(id=self.request.user.id)
        else:
            return qs.none()
        
    def initial(self, request, *args, **kwargs):
        if self.permission_classes and len(self.permission_classes):
            pass
        elif request.method in permissions.SAFE_METHODS:
            self.permission_classes = (permissions.AllowAny,)
        else:
            self.permission_classes = [IsSuperAdminUser|IsAdminUser]
        return super(UserViewSet, self).initial(request, *args, **kwargs)
    

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
        elif request.user.is_admin:
            user = self.get_object()
            if user.institution == request.user.institution:
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
                        "error": "User not in your institution",
                        "code": "permission-deny"
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
        if user is None: 
            return Response(status=status.HTTP_404_NOT_FOUND)
        if user.is_authenticated:
            if user.is_deleted:
                return Response(status=status.HTTP_410_GONE)
            return Response(UserSerializer(user).data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    