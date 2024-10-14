from django.db import models
from django.conf import settings
from cognigrade.utils.models import BaseModel
from cognigrade.accounts.choices import RoleChoices

class Institutions(BaseModel):
    name = models.CharField(
        max_length=50
    )
    location = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    latitude = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    longitude = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    @property
    def institution_admins(self):
        return self.users.filter(role=RoleChoices.ADMIN)
    
    @property
    def institution_teachers(self):
        return self.users.filter(role=RoleChoices.TEACHER)
    
    @property
    def institution_students(self):
        return self.users.filter(role=RoleChoices.STUDENT)


    class Meta:
        db_table = f'{settings.DB_PREFIX}_institutions'