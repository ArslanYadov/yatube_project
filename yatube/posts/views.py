from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, Group, User
from django.db.models import Count


POSTS_AMOUNT = 10


def index(request):
    paginator = (
        Paginator(
            Post.objects
            .select_related('author', 'group'),
            POSTS_AMOUNT
        )
    )
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_obj,}
    )


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


def profile(request, username):
    paginator = (
        Paginator(
            Post.objects.
            select_related('author', 'group')
            .filter(author__username=username),
            POSTS_AMOUNT
        )
    )
    page_obj = paginator.get_page(request.GET.get('page'))
    user = User.objects.get(username=username)
    amount = Post.objects.filter(author__username=username).count()
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': page_obj,
            'user': user,
            'amount': amount,
        }
    )


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    amount = (
        Post.objects
        .filter(author__username=post.author)
        .annotate(count=Count('author'))
    )
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'amount': amount,
        }
    )


def post_create(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            Post.objects.create(text=text, author=user, group=group)
            return redirect(f'/profile/{username}/')
        return render(
            request,
            'posts/create_post.html',
            {'form': form}
        )
    form = PostForm()
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    ) 