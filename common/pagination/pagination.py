from rest_framework.pagination import PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReferenceDataPagination(DefaultPageNumberPagination):
    """For the catalogues a picker loads whole rather than a page at a time.

    The cruise search derives its country list from the ports it has, so a page
    cap silently shortens that list: at the default hundred it was offering
    fifty-odd of the catalogue's hundred countries and no error anywhere said
    so. These rows are short, few, and change about once a year.
    """

    page_size = 100
    max_page_size = 1000
