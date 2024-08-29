from django.db import models

class RoleChoices(models.TextChoices):
    """Define the choices for the role field."""
    SUPERADMIN = 'superadmin', 'Super Admin'
    ADMIN = 'admin', 'Admin'
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
