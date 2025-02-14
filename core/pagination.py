from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        page_size = self.get_page_size(self.request)

        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
                "page_size": page_size if page_size != self.max_page_size else "all",
            }
        )

    def get_page_size(self, request):
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size == "all":
            return self.max_page_size
        return super().get_page_size(request)
