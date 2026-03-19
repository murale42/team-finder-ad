from django.core.paginator import Paginator
from team_finder.constants import PROJECTS_PER_PAGE


# Сервис для пагинации проектов
def paginate_queryset(queryset, request, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
