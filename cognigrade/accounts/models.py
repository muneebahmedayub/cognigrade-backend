from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from cognigrade.institutions.models import Institutions
from .choices import RoleChoices
from .managers import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """Define the custom user model."""

    first_name = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=50,
        choices=RoleChoices.choices,
        default=RoleChoices.STUDENT
    )
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(
        default=True
    )

    is_deleted = models.BooleanField(
        default=False
    )
    deleted_on = models.DateTimeField(
        null=True,
        blank=True
    )
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_by_user'
    )

    institution = models.ForeignKey(
        'institutions.Institutions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='institution_admin'
    )

    @property
    def is_superadmin(self):
        return self.role == RoleChoices.SUPERADMIN
    
    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN
    
    @property
    def is_teacher(self):
        return self.role == RoleChoices.TEACHER
    
    @property
    def is_student(self):
        return self.role == RoleChoices.STUDENT

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = f'{settings.DB_PREFIX}_user'