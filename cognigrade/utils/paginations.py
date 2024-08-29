# at spacium/utils/paginations.py
from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PagePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 30

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', self.page.number),
            ('num_pages', self.page.paginator.num_pages),
            ('recordsTotal', self.page.paginator.count),
            ('recordsFiltered', self.page.paginator.per_page),
            ('previous', self.get_previous_link()),
            ('next_url', self.get_next_link()),
            ('results', data)
        ]))