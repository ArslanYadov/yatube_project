from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm
from .models import Post, Group, User
from yatube.settings import POSTS_AMOUNT_PER_PAGE


def get_context(request, queryset):
    paginator = Paginator(queryset, POSTS_AMOUNT_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return {'page_obj': page_obj,}


def index(request):
    context = get_context(
        request,
        Post.objects
        .select_related('author', 'group')
    )
    return render(
        request,
        'posts/index.html',
        context
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {'group': group,}
    context.update(
        get_context(
            request,
            group.posts.all()
        )
    )
    return render(
        request,
        'posts/group_list.html',
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {'author': author,}
    context.update(
        get_context(
            request,
            author.posts.all()
        )
    )
    return render(
        request,
        'posts/profile.html',
        context
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        'posts/post_detail.html',
        {'post': post,}
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(
        request,
        'posts/create_post.html',
        {'form': form,}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if request.method == "POST" and form.is_valid():
        form.save(commit=True)
        return redirect('posts:post_detail', post_id)
    return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
                'post': post,
            }
        )
