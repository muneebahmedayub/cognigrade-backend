from django.db import models

class RoleChoices(models.TextChoices):
    """Define the choices for the role field."""
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'
