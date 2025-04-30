from django.db import models
from cognigrade.utils.models import BaseModel
from cognigrade.courses.models import Classroom
from cognigrade.accounts.models import User


class OMR(BaseModel):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)


class OMRQuestions(BaseModel):
    omr = models.ForeignKey(OMR, on_delete=models.CASCADE, related_name='questions')
    answer = models.IntegerField(choices=[(i, i) for i in range(1, 5)])

class OMRSubmission(BaseModel):
    omr = models.ForeignKey(OMR, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='omr_submissions')
    score = models.IntegerField()
    
