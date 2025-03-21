from django_filters import rest_framework as filters


class BaseOrderBy(filters.FilterSet):
    order_by = filters.CharFilter(method="order_by_filter")

    def order_by_filter(self, qs, name, value):
        return qs.order_by(value)


class BaseCreateUpdatedOnFilter(filters.FilterSet):
    created_after = filters.CharFilter(field_name='created_on', lookup_expr='date__gte')
    created_before = filters.CharFilter(field_name='created_on', lookup_expr='date__lte')
    updated_after = filters.CharFilter(field_name='updated_on', lookup_expr='date__gte')
    updated_before = filters.CharFilter(field_name='updated_on', lookup_expr='date__lte')
