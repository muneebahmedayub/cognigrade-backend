from django.db import models
from django.conf import settings
from cognigrade.institutions.models import Institutions
from cognigrade.accounts.models import User
from cognigrade.utils.models import BaseModel
from django.core.exceptions import ValidationError

class Course(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    institution = models.ForeignKey(Institutions, on_delete=models.CASCADE, related_name='courses')

    class Meta:
        db_table = f'{settings.DB_PREFIX}_courses'


class Classroom(BaseModel):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classrooms')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='assigned_classrooms'
    )
    enrollments = models.ManyToManyField(User, related_name='classrooms', limit_choices_to={'role': 'student'})

    def clean(self):
        for enrollment in self.enrollments:
            if enrollment.role != 'student':
                raise ValidationError('Only users with students role can be enrolled to a classroom')
        if self.teacher.role != 'teacher':
            raise ValidationError('Only users with teacher role can be assigned to a classroom.')

    class Meta:
        db_table = f'{settings.DB_PREFIX}_classrooms'
