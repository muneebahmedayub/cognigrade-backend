from cognigrade.utils.filters import BaseOrderBy, BaseCreateUpdatedOnFilter
from .models import Course, Classroom

class CourseFilter(BaseOrderBy, BaseCreateUpdatedOnFilter):
    class Meta:
        model = Course
        fields = '__all__'

class ClassroomFilter(BaseOrderBy, BaseCreateUpdatedOnFilter):
    class Meta:
        model = Classroom
        fields = '__all__'
