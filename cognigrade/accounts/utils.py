from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

def delete_user(user, request):
    deleted_by = request.user
    user.is_deleted = True
    user.deleted_on = timezone.now()
    user.deleted_by = deleted_by
    user.is_active = False
    user.save()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }