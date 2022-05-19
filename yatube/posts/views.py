from multiprocessing import context
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Post, Group


POSTS_AMOUNT = 10


def index(request):
    paginator = (
        Paginator(
            Post.objects.
            select_related('author', 'group'),
            POSTS_AMOUNT
        )
    )
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'posts/index.html', {'page_obj': page_obj,})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = (
        Paginator(
            group.posts.all(),
            POSTS_AMOUNT
        )
    )
    page_obj = posts.get_page(request.GET.get('page'))
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        }
    )
