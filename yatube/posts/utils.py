from django.core.paginator import Paginator
from yatube.settings import POSTS_AMOUNT_PER_PAGE


def paginate_page(request, posts_list):
    """Паджинация постов по 10 штук на страницу."""
    paginator = Paginator(posts_list, POSTS_AMOUNT_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
