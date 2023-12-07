from rest_framework.pagination import PageNumberPagination


class LimitPaginator(PageNumberPagination):
    """Кастомная пагинация страниц."""
    page_size_query_param = 'limit'
