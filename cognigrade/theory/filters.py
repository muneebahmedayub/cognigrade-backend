from django_filters import rest_framework as filters
from .models import Theory, TheoryType, TheorySubmission
from cognigrade.utils.filters import BaseCreateUpdatedOnFilter

class TheoryFilter(BaseCreateUpdatedOnFilter):
    title = filters.CharFilter(lookup_expr='icontains')
    type = filters.ChoiceFilter(choices=TheoryType.choices)
    classroom = filters.NumberFilter()

    class Meta:
        model = Theory
        fields = ['classroom', 'type', 'title', 'created_after', 'created_before', 'updated_after', 'updated_before'] 

class TheorySubmissionFilter(BaseCreateUpdatedOnFilter):
    theory = filters.NumberFilter()
    student = filters.NumberFilter()

    class Meta:
        model = TheorySubmission
        fields = ['theory', 'student', 'created_after', 'created_before', 'updated_after', 'updated_before']