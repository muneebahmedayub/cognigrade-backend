from django.db import models
from cognigrade.utils.models import BaseModel
from cognigrade.courses.models import Classroom
from cognigrade.accounts.models import User

class TheoryType(models.TextChoices):
    ASSIGNMENT = 'assignment'
    QUIZ = 'quiz'
    EXAM = 'exam'


class Theory(BaseModel):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TheoryType.choices)


class TheoryQuestions(BaseModel):
    theory = models.ForeignKey(Theory, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField()
    options = models.JSONField(default=list)