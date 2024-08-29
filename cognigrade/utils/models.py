from django.db import models

# Create your models here.

class BaseModel(models.Model):
    """Define all common fields for all table."""

    created_on = models.DateTimeField(
        auto_now_add=True
    )  # object creation time. will automatic generate
    updated_on = models.DateTimeField(
        auto_now=True
    )  # object update time. will automatic generate

    class Meta:
        abstract = True  # define this table/model is abstract.
