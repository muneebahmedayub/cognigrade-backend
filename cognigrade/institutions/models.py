from django.db import models
from django.conf import settings
from cognigrade.utils.models import BaseModel

class Institutions(BaseModel):
    name = models.CharField(
        max_length=50
    )
    location = models.CharField(
        max_length=50
    )
    latitude = models.CharField(
        max_length=50
    )
    longitude = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = f'{settings.DB_PREFIX}_institutions'