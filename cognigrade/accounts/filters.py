from django_filters import rest_framework as filters

from cognigrade.utils.filters import BaseOrderBy, BaseCreateUpdatedOnFilter

from .models import User, RoleChoices
from cognigrade.institutions.models import Institutions

class UserFilter(BaseOrderBy, BaseCreateUpdatedOnFilter):
    is_deleted = filters.BooleanFilter(field_name='is_deleted', lookup_expr='exact')
    role = filters.ChoiceFilter(choices=RoleChoices.choices)
    institution = filters.ModelChoiceFilter(queryset=Institutions.objects.all())
    class Meta:
        model = User
        fields = ['is_deleted', 'role', 'institution']