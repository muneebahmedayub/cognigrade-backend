# at carbackend/backend/users/managers.py
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_base(
        self,
        email,
        password,
        is_superuser,
        **extra_fields
    ) -> object:
        """
        Create User With Email name password
        """
        if not email:
            raise ValueError("User must have an email")
        user = self.model(
            email=email,
            is_superuser=is_superuser,
            role="superadmin" if is_superuser else "ADMIN",
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ) -> object:
        """Creates and save non-staff-normal user
        with given email, username and password."""

        return self.create_base(
            email,
            password,
            False,
            **extra_fields
        )

    def create_superuser(
        self,
        email,
        password,
        **extra_fields
    ) -> object:
        """Creates and saves super user
        with given email, name and password."""
        return self.create_base(
            email,
            password,
            True,
            **extra_fields
        )

    def get_or_create_dummy(self, email) -> object:
        if not email:
            return None
        try:
            return self.get(email=email)
        except self.model.DoesNotExist:
            return self.create_user(email=email, is_active=False)
