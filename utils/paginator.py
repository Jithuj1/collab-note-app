from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = settings.PAGINATION_PAGE_SIZE
    page_size_query_param = "length"

    def get_paginated_response(self, object_name, data):
        resp_data = {
            "success": True,
            "data": {object_name: data},
            "pagination": {
                "total_count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
            },
        }

        return Response(resp_data)
