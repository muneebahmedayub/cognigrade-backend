from django.db import models
from cognigrade.utils.models import BaseModel
from cognigrade.institutions.models import Institutions
from cognigrade.accounts.models import User


class OMR(BaseModel):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Institutions, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)


class OMRQuestions(BaseModel):
    omr = models.ForeignKey(OMR, on_delete=models.CASCADE)
    answer = models.IntegerField(choices=[(i, i) for i in range(1, 5)])