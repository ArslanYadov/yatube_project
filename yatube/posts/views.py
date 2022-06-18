from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Post, Group, User
from .utils import paginate_page


@cache_page(20, key_prefix='index_page')
def index(request):
    """Отображает все посты, включая те, у которых есть группа."""
    posts = Post.objects.select_related('author', 'group')
    page_obj = paginate_page(request, posts)
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_obj, }
    )


def group_posts(request, slug):
    """Отображает все посты из группы, определенной по slug."""
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate_page(request, group.posts.all())
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page_obj,
        }
    )


def profile(request, username):
    """Отображает посты пользователя, определенного по username."""
    author = get_object_or_404(User, username=username)
    page_obj = paginate_page(request, author.posts.all())
    following = request.user.is_authenticated and author.following.exists()
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page_obj,
            'following': following
        }
    )


def post_detail(request, post_id):
    """
    Отображает единичный пост, выбранный по post_id.
    Показывает список комментариев, если они есть.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
        }
    )


@login_required
def post_create(request):
    """
    Выводит форму для создания поста с полями:
    'Текст', 'Группа' и 'Загрузить картинку'.
    Декотратор отправляет неавторизованного пользователя залогиниться.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
    }
    if not request.method == 'POST':
        return render(
            request,
            'posts/create_post.html',
            context
        )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            context
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    """
    Выводит форму для редактирования поста с проверкой,
    что пост принадлежит пользователю.
    Декотратор отправляет неавторизованного пользователя залогиниться.
    """
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'post': post,
    }
    if not request.method == 'POST':
        return render(
            request,
            'posts/create_post.html',
            context
        )
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            context
        )
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate_page(request, posts)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user or author.following.exists():
        return redirect('posts:profile', username)
    author.following.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if not author.following.exists():
        return redirect('posts:profile', username)
    author.following.all().delete()
    return redirect('posts:profile', username)
